from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Restaurant, Menu
from .views import complete_restaurant_profile
from .forms import RestaurantForm
from myproject.articles.models import Article

User = get_user_model()


class CompleteRestaurantProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User._default_manager._create_user(
            username='restaurantuser',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.url = reverse('complete_restaurant_profile')

    def test_redirects_if_not_restaurant_type(self):
        # Тест за пренасочване при user
        user = User._default_manager._create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123',
            type='user'
        )
        request = self.factory.get(self.url)
        request.user = user
        response = complete_restaurant_profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete_user_profile'))

        # Тест за пренасочване при supplier
        supplier = User._default_manager._create_user(
            username='supplier',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        request = self.factory.get(self.url)
        request.user = supplier
        response = complete_restaurant_profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete_supplier_profile'))

    def test_creates_restaurant_for_new_user(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], RestaurantForm)
        self.assertFalse(response.context['is_update'])

        # Тестваме създаване на ресторант
        form_data = {
            'name': 'Test Restaurant',
            'phone_number': '1234567890',
            'address': 'Test Address',
        }
        response = self.client.post(self.url, {**form_data,})
        self.assertEqual(response.status_code, 302)

        restaurant = Restaurant.objects.get(account=self.user)
        self.assertEqual(restaurant.name, 'Test Restaurant')
        self.assertEqual(restaurant.phone_number, '1234567890')
        self.assertEqual(restaurant.address, 'Test Address')

    def test_updates_existing_restaurant(self):
        # Първо създаваме ресторант
        restaurant = Restaurant.objects.create(
            account=self.user,
            name='Old Name',
            phone_number='123',
            address='Old Address'
        )

        self.client.login(email='restaurant@example.com', password='testpass123')
        form_data = {
            'name': 'New Name',
            'phone_number': '987654321',
            'address': 'New Address',
        }
        response = self.client.post(self.url, form_data)

        restaurant.refresh_from_db()
        self.assertEqual(restaurant.name, 'New Name')
        self.assertEqual(restaurant.phone_number, '987654321')
        self.assertEqual(restaurant.address, 'New Address')


class RestaurantHomeViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='restaurantuser',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.restaurant = Restaurant.objects.create(
            account=self.user,
            name='Test Restaurant',
            phone_number='1234567890',
            address='Test Address'
        )
        self.url = reverse('restaurant_home_view', kwargs={'pk': self.restaurant.pk})

    def test_access_by_owner(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['restaurant'], self.restaurant)
        self.assertEqual(response.context['profile_type'], 'Restaurant')

    def test_access_by_non_owner(self):
        other_user = User._default_manager._create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied

    def test_access_by_wrong_user_type(self):
        user = User._default_manager._create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123',
            type='user'
        )
        self.client.login(email='user@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied


class EditRestaurantViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='restaurantuser',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.restaurant = Restaurant.objects.create(
            account=self.user,
            name='Test Restaurant',
            phone_number='1234567890',
            address='Test Address'
        )
        self.url = reverse('edit_restaurant', kwargs={'pk': self.restaurant.pk})

    def test_updates_restaurant(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        form_data = {
            'name': 'Updated Name',
            'phone_number': '987654321',
            'address': 'Updated Address',
            'delivery_fee': '2.50',
            'discount': '10.00'
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)

        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.name, 'Updated Name')
        self.assertEqual(self.restaurant.phone_number, '987654321')
        self.assertEqual(self.restaurant.address, 'Updated Address')
        self.assertEqual(str(self.restaurant.delivery_fee), '2.50')
        self.assertEqual(str(self.restaurant.discount), '10.00')


class MenuDetailsViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='restaurantuser',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.restaurant = Restaurant.objects.create(
            account=self.user,
            name='Test Restaurant',
            phone_number='1234567890',
            address='Test Address'
        )
        Menu.objects.filter(restaurant=self.restaurant).delete()
        self.menu = Menu.objects.create(
            restaurant=self.restaurant,
            name='Test Menu'
        )
        self.article = Article.objects.create(
            menu=self.menu,
            name='Test Article',
            price=10.00
        )
        self.url = reverse('restaurant_menu', kwargs={'pk': self.restaurant.pk})

    def test_access_by_owner(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['menu'], self.menu)

    def test_access_by_non_owner(self):
        other_user = User._default_manager._create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied


class RestaurantMenuViewForUsersTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='restaurantuser',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.restaurant = Restaurant.objects.create(
            account=self.user,
            name='Test Restaurant',
            phone_number='1234567890',
            address='Test Address'
        )
        # Изтриваме автоматично създадените менюта от сигналите
        Menu.objects.filter(restaurant=self.restaurant).delete()
        # Създаваме само едно меню
        self.menu = Menu.objects.create(
            restaurant=self.restaurant,
            name='Test Menu'
        )
        self.article = Article.objects.create(
            menu=self.menu,
            name='Test Article',
            price=10.00
        )
        self.url = reverse('restaurant_menu', kwargs={'pk': self.restaurant.pk})


    def test_access_by_owner(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['menu'], self.menu)

    def test_access_by_restaurant(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # PermissionYES

    def test_access_by_supplier(self):
        supplier = User._default_manager._create_user(
            username='supplier',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied


class RestaurantOrdersViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='restaurantuser',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        self.restaurant = Restaurant.objects.create(
            account=self.user,
            name='Test Restaurant',
            phone_number='1234567890',
            address='Test Address'
        )
        self.url = reverse('restaurant_orders')

    def test_access_by_restaurant(self):
        self.client.login(email='restaurant@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pending_orders']), 0)
        self.assertEqual(len(response.context['ready_orders']), 0)
        self.assertEqual(len(response.context['delivered_orders']), 0)

    def test_access_by_non_restaurant(self):
        user = User._default_manager._create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123',
            type='user'
        )
        self.client.login(email='user@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied

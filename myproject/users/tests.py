from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import PermissionDenied

from .models import UserProfile
from .views import complete_user_profile
from .forms import UserProfileForm
from myproject.orders.models import Cart
from myproject.restaurants.models import Restaurant

User = get_user_model()


class CompleteUserProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User._default_manager._create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            type='user'
        )
        self.url = reverse('complete_user_profile')

    def test_redirects_if_not_user_type(self):
        # Тест за пренасочване при supplier
        supplier = User._default_manager._create_user(
            username='supplier',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        request = self.factory.get(self.url)
        request.user = supplier
        response = complete_user_profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete_supplier_profile'))

        # Тест за пренасочване при restaurant
        restaurant = User._default_manager._create_user(
            username='restaurant',
            email='restaurant@example.com',
            type='restaurant',
            password='testpass123'
        )
        request = self.factory.get(self.url)
        request.user = restaurant
        response = complete_user_profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete_restaurant_profile'))
    #
    def test_creates_profile_for_new_user(self):
    # Изтриваме автоматично създадения профил от сигнала, ако съществува

        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserProfileForm)

        # Тестваме създаване на профил
        form_data = {
            'account': self.user,
            'name': 'Test User',
            'phone_number': '1234567890',
            'address': 'Test Address',
        }
        response = self.client.post(self.url, {**form_data})

        # Проверяваме дали е пренасочен успешно
        self.assertEqual(response.status_code, 302)

        # Проверяваме дали профилът е създаден
        self.assertTrue(UserProfile.objects.filter(account=self.user).exists())
        profile = UserProfile.objects.get(account=self.user)

        # Проверяваме данните на профила
        self.assertEqual(profile.name, 'Test User')
        self.assertEqual(profile.phone_number, '1234567890')
        self.assertEqual(profile.address, 'Test Address')

        # Проверяваме дали е създадена количка
        self.assertTrue(hasattr(profile, 'cart'))

    def test_updates_existing_profile(self):
        # Използваме вече създадения профил от сигнала
        profile = UserProfile.objects.get(account=self.user)
        profile.name = 'Old Name'
        profile.phone_number = '123'
        profile.address = 'Old Address'
        profile.save()

        self.client.login(email='test@example.com', password='testpass123')
        form_data = {
            'name': 'New Name',
            'phone_number': '987654321',
            'address': 'New Address',
        }
        response = self.client.post(self.url, form_data)

        profile.refresh_from_db()
        self.assertEqual(profile.name, 'New Name')
        self.assertEqual(profile.phone_number, '987654321')
        self.assertEqual(profile.address, 'New Address')


class RegularUserHomeViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            type='user'
        )
        self.profile = UserProfile.objects.get(account=self.user)
        self.url = reverse('user_home', kwargs={'pk': self.profile.pk})
        self.restaurant = Restaurant.objects.create(
            account=self.user,
            name='Test Restaurant',
            address='Test Address',
            phone_number='1234567890'
        )

    def test_access_by_owner(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['userprofile'], self.profile)
        self.assertEqual(response.context['profile_type'], 'RegularUser')
        self.assertIn(self.restaurant, response.context['restaurants'])

    def test_access_by_non_owner(self):
        other_user = User._default_manager._create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            type='user'
        )
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied

    def test_access_by_wrong_user_type(self):
        supplier = User._default_manager._create_user(
            username='supplier',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            type='user'
        )
        self.profile = UserProfile.objects.get(account=self.user)
        self.url = reverse('user_profile', kwargs={'pk': self.user.pk})

    def test_view_renders_correctly(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.profile)


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            type='user'
        )
        self.profile = UserProfile.objects.get(account=self.user)
        self.url = reverse('user_profile_edit', kwargs={'pk': self.user.pk})

    def test_updates_profile(self):
        self.client.login(email='test@example.com', password='testpass123')
        form_data = {
            'name': 'Updated Name',
            'phone_number': '987654321',
            'address': 'Updated Address',
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'Updated Name')
        self.assertEqual(self.profile.phone_number, '987654321')
        self.assertEqual(self.profile.address, 'Updated Address')


class UserOrdersViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            type='user'
        )
        self.profile = UserProfile.objects.get(account=self.user)
        self.url = reverse('user_orders')

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Пренасочва към логин

    def test_renders_for_logged_in_user(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

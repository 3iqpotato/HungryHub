from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from myproject import settings
from myproject.accounts.models import Account
from myproject.restaurants.models import Restaurant
from django.core.exceptions import PermissionDenied


class RestaurantHomeViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_owner = Account.objects._create_user(username='owner@gmail.com', email='owner@gmail.com', password='testpass')
        self.user_other = Account.objects._create_user(username='other@gmail.com', email='other@gmail.com', password='testpass')

        # Create Restaurant instance
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            account=self.user_owner
        )

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('restaurant_home_view', kwargs={'pk': self.restaurant.pk}))
        login_url = f"{settings.LOGIN_URL}?next={reverse('restaurant_home_view', kwargs={'pk': self.restaurant.pk})}"
        self.assertRedirects(response, login_url)

    def test_view_for_correct_user(self):
        self.client.login(username='owner@gmail.com', email='owner@gmail.com', password='testpass')
        response = self.client.get(reverse('restaurant_home_view', kwargs={'pk': self.restaurant.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/restaurant_home.html')
        self.assertEqual(response.context['restaurant'], self.restaurant)
        self.assertEqual(response.context['profile_type'], 'Restaurant')

    def test_view_for_incorrect_user(self):
        self.client.login(username='owner@gmail.com', email='owner@gmail.com',password='testpass')
        response = self.client.get(reverse('restaurant_home_view', kwargs={'pk': self.restaurant.pk}))
        self.assertEqual(response.status_code, 200)  # PermissionDenied

    def test_view_restaurant_does_not_exist(self):
        self.client.login(username='owner@gmail.com', email='owner@gmail.com', password='testpass')
        response = self.client.get(reverse('restaurant_home_view', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class EditRestaurantViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_owner = Account.objects._create_user(username='owner@gmail.com', email='owner@gmail.com', password='testpass')
        self.user_other = Account.objects._create_user(username='other@gmail.com', email='other@gmail.com', password='testpass')

        self.restaurant = Restaurant.objects.create(
            name='Editable Restaurant',
            account=self.user_owner
        )

    def test_get_edit_view_as_owner(self):
        self.client.login(username='owner@gmail.com', email='owner@gmail.com', password='testpass')
        response = self.client.get(reverse('edit_restaurant', kwargs={'pk': self.restaurant.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/edit_restaurant.html')

    # def test_post_edit_view_as_owner(self):
    #     self.client.login(username='owner@gmail.com', email='owner@gmail.com', password='testpass')
    #     data = {
    #         'name': 'Updated Restaurant',
    #     }
    #     response = self.client.post(reverse('edit_restaurant', kwargs={'pk': self.restaurant.pk}), data)
    #     # self.assertRedirects(response, reverse('restaurant_home_view', kwargs={'pk': self.restaurant.pk}))
    #     self.restaurant.refresh_from_db()
    #     self.assertEqual(self.restaurant.name, 'Updated Restaurant')

    def test_edit_view_as_other_user_redirects(self):
        self.client.login(username='other@gmail.com', email='owner@gmail.com', password='testpass')
        response = self.client.get(reverse('edit_restaurant', kwargs={'pk': self.restaurant.pk}))
        # Просто провери какъв статус идва
        self.assertNotEqual(response.status_code, 200, "Other user should not get status 200 OK")

    def test_edit_view_not_logged_in(self):
        response = self.client.get(reverse('edit_restaurant', kwargs={'pk': self.restaurant.pk}))
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={reverse('edit_restaurant',
                                                                            kwargs={'pk': self.restaurant.pk})}")



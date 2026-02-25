from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Supplier
from .views import complete_supplier_profile
from .forms import SupplierForm

User = get_user_model()


class CompleteSupplierProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User._default_manager._create_user(
            username='supplieruser',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.url = reverse('complete_supplier_profile')

    def test_redirects_if_not_supplier_type(self):
        # Тест за пренасочване при user
        user = User._default_manager._create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123',
            type='user'
        )
        request = self.factory.get(self.url)
        request.user = user
        response = complete_supplier_profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete_user_profile'))

        # Тест за пренасочване при restaurant
        restaurant = User._default_manager._create_user(
            username='restaurant',
            email='restaurant@example.com',
            password='testpass123',
            type='restaurant'
        )
        request = self.factory.get(self.url)
        request.user = restaurant
        response = complete_supplier_profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete_restaurant_profile'))

    def test_creates_supplier_for_new_user(self):
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SupplierForm)

        # Тестваме създаване на доставчик

        form_data = {
            'name': 'Test Supplier',
            'phone_number': '1234567890',
            'type': 'car',
        }
        response = self.client.post(self.url, {**form_data,})

        # Проверяваме дали е пренасочен успешно
        self.assertEqual(response.status_code, 302)

        # Проверяваме дали доставчикът е създаден
        self.assertTrue(Supplier.objects.filter(account=self.user).exists())
        supplier = Supplier.objects.get(account=self.user)
        self.assertEqual(supplier.name, 'Test Supplier')
        self.assertEqual(supplier.phone_number, '1234567890')
        self.assertEqual(supplier.type, 'car')

    # def test_updates_existing_supplier(self):
    #     # Първо създаваме доставчик
    #     supplier = Supplier.objects.create(
    #         account=self.user,
    #         name='Old Name',
    #         phone_number='123',
    #         type='Old Type',
    #     )
    #
    #     self.client.login(email='supplier@example.com', password='testpass123')
    #     form_data = {
    #         'name': 'New Name',
    #         'phone_number': '987654321',
    #         'type': 'New Type',
    #     }
    #     response = self.client.post(reverse('edit_supplier_profile'), form_data)
    #     self.assertEqual(response.status_code, 302)
    #
    #     supplier.refresh_from_db()
    #     self.assertEqual(supplier.name, 'New Name')
    #     self.assertEqual(supplier.phone_number, '987654321')
    #     self.assertEqual(supplier.type, 'New Type')


class EditSupplierProfileViewTests(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='supplieruser',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.url = reverse('edit_supplier_profile')

    def test_updates_existing_supplier(self):
        supplier = Supplier.objects.create(
            account=self.user,
            name='Old Name',
            phone_number='123',
            type='motorcycle',
        )

        self.client.login(email='supplier@example.com', password='testpass123')
        form_data = {
            'name': 'New Name',
            'phone_number': '987654321',
            'type': 'car',
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)

        supplier.refresh_from_db()
        self.assertEqual(supplier.name, 'New Name')
        self.assertEqual(supplier.phone_number, '987654321')
        self.assertEqual(supplier.type, 'car')

class SupplierHomeViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='supplieruser',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.supplier = Supplier.objects.create(
            account=self.user,
            name='Test Supplier',
            phone_number='1234567890',
            type='car',
        )
        self.url = reverse('supplier_home_view')

    def test_access_by_supplier(self):
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_by_non_supplier(self):
        user = User._default_manager._create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123',
            type='user'
        )
        self.client.login(email='user@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied


class EditSupplierProfileViewTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='supplieruser',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.supplier = Supplier.objects.create(
            account=self.user,
            name='Test Supplier',
            phone_number='1234567890',
            type='car',
        )
        self.url = reverse('edit_supplier_profile')

    def test_updates_supplier_profile(self):
        self.client.login(email='supplier@example.com', password='testpass123')
        form_data = {
            'name': 'Updated Name',
            'phone_number': '987654321',
            'type': 'motorcycle',
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)

        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, 'Updated Name')
        self.assertEqual(self.supplier.phone_number, '987654321')
        self.assertEqual(self.supplier.type, 'motorcycle')


class SupplierOrderViewsTest(TestCase):
    def setUp(self):
        self.user = User._default_manager._create_user(
            username='supplieruser',
            email='supplier@example.com',
            password='testpass123',
            type='supplier'
        )
        self.supplier = Supplier.objects.create(
            account=self.user,
            name='Test Supplier',
            phone_number='1234567890',
            type='car',
        )

    def test_available_orders_view(self):
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(reverse('available_orders'))
        self.assertEqual(response.status_code, 200)

    def test_active_orders_view(self):
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(reverse('supplier_active_orders'))
        self.assertEqual(response.status_code, 200)

    def test_delivered_orders_view(self):
        self.client.login(email='supplier@example.com', password='testpass123')
        response = self.client.get(reverse('supplier_delivered_orders'))
        self.assertEqual(response.status_code, 200)

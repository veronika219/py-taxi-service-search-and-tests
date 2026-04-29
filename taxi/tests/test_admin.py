from django.test import TestCase, Client
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from taxi.models import Car, Driver, Manufacturer


class AdminSiteTest(TestCase):
    def setUp(self):
        self.client_admin = Client()
        self.client_driver = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="test123"
        )

        self.driver = get_user_model().objects.create_user(
            username="driver", password="test123", license_number="ABC123"
        )

        self.client_admin.force_login(self.admin_user)
        self.client_driver.force_login(self.driver)

    def test_car_registered_in_admin(self):
        self.assertIn(Car, admin.site._registry)

    def test_driver_registered_in_admin(self):
        self.assertIn(Driver, admin.site._registry)

    def test_manufacturer_registered_in_admin(self):
        self.assertIn(Manufacturer, admin.site._registry)

    def test_driver_license_number_listed(self):
        """
        Test that driver's license is in display_list on the admin page
        :return:
        """
        url = reverse("admin:taxi_driver_changelist")
        res = self.client_admin.get(url)
        self.assertContains(res, self.driver.license_number)

    def test_driver_detail_license_number_listed(self):
        """
        Test that driver's license is in fieldset on the detail admin page
        :return:
        """
        url = reverse("admin:taxi_driver_change", args=[self.driver.id])
        res = self.client_admin.get(url)
        self.assertContains(res, self.driver.license_number)

    def test_car_search_fields(self):
        admin_obj = admin.site._registry[Car]
        self.assertIn("model", admin_obj.search_fields)

    def test_car_list_filter(self):
        admin_obj = admin.site._registry[Car]
        self.assertIn("manufacturer", admin_obj.list_filter)

    def test_admin_required_login(self):
        url = reverse("admin:taxi_driver_changelist")
        res_driver = self.client_driver.get(url)
        self.assertEqual(res_driver.status_code, 302)

    def test_login_success(self):
        url = reverse("admin:taxi_driver_changelist")
        res_admin = self.client_admin.get(url)
        self.assertEqual(res_admin.status_code, 200)

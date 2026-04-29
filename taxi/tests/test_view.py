from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from taxi.models import Manufacturer

MANUFACTURER_URL = reverse("taxi:manufacturer-list")


class PublicManufacturerTest(TestCase):
    def test_login_required(self):
        res = Client().get(MANUFACTURER_URL)
        self.assertEqual(res.status_code, 302)


class PublicDriverTest(TestCase):
    def test_login_required(self):
        res = Client().get(reverse("taxi:driver-list"))
        self.assertEqual(res.status_code, 302)


class PrivateDriverTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test",
            first_name="first test",
            last_name="last test",
            password="test123",
            license_number="ABC12334",
        )
        self.client.force_login(self.user)

    def test_retrieve_drivers(self):
        get_user_model().objects.create_user(
            username="test1", password="test123", license_number="ABC234"
        )

        get_user_model().objects.create_user(
            username="test2", password="test123", license_number="DFG234"
        )

        drivers = get_user_model().objects.all()
        res = self.client.get(reverse("taxi:driver-list"))
        self.assertEqual(list(res.context["driver_list"]), list(drivers))

    def test_driver_login_success(self):
        res = self.client.get(reverse("taxi:driver-list"))
        self.assertEqual(res.status_code, 200)

    def test_driver_template(self):
        res = self.client.get(reverse("taxi:driver-list"))
        self.assertTemplateUsed(res, "taxi/driver_list.html")

    def test_driver_form_data(self):
        form_data = {
            "username": "usertest",
            "license_number": "ABC12344",
            "first_name": "first",
            "last_name": "last",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }

        self.client.post(reverse("taxi:driver-create"), data=form_data)
        new_driver = get_user_model().objects.get(username=form_data["username"])

        self.assertEqual(new_driver.username, form_data["username"])
        self.assertEqual(new_driver.first_name, form_data["first_name"])
        self.assertEqual(new_driver.last_name, form_data["last_name"])
        self.assertEqual(new_driver.license_number, form_data["license_number"])

        self.assertTrue(new_driver.check_password(form_data["password1"]))


class PrivateManufacturerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test", password="test123"
        )
        self.client.force_login(self.user)

    def test_retrieve_manufacturers(self):
        Manufacturer.objects.create(name="test1", country="test")

        Manufacturer.objects.create(name="test2", country="test")
        manufacturers = Manufacturer.objects.all()
        res = self.client.get(MANUFACTURER_URL)

        self.assertEqual(list(res.context["manufacturer_list"]), list(manufacturers))

    def test_manufacturer_template(self):
        res = self.client.get(reverse("taxi:manufacturer-list"))
        self.assertTemplateUsed(res, "taxi/manufacturer_list.html")

    def test_login_required_success(self):
        res = self.client.get(MANUFACTURER_URL)
        self.assertEqual(res.status_code, 200)

    def test_create_manufacturer(self):
        form_data = {"name": "test", "country": "test country"}
        self.client.post(reverse("taxi:manufacturer-create"), data=form_data)

        new_manufacturer = Manufacturer.objects.get(name=form_data["name"])

        self.assertEqual(new_manufacturer.name, form_data["name"])
        self.assertEqual(new_manufacturer.country, form_data["country"])

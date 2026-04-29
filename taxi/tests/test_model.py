from wsgiref.validate import assert_

from django.contrib.auth import get_user_model
from django.test import TestCase
from taxi.models import Manufacturer, Driver, Car
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class ModelsTest(TestCase):
    def test_manufacturer_str(self):
        manufacturer = Manufacturer.objects.create(name="test", country="test")
        self.assertEqual(
            str(manufacturer), f"{manufacturer.name} {manufacturer.country}"
        )

    def test_manufacturer_create_object(self):
        manufacturer = Manufacturer.objects.create(name="test", country="Ukraine")

        self.assertEqual(manufacturer.name, "test")
        self.assertEqual(manufacturer.country, "Ukraine")
        self.assertIsNotNone(manufacturer.pk)

    def test_manufacturer_unique_name(self):
        manufacturer = Manufacturer.objects.create(name="UnigueValue", country="test")
        # Обробка помилки, наприклад, повернення повідомлення "Користувач вже існує"
        with self.assertRaises(IntegrityError):
            Manufacturer.objects.create(name="UnigueValue", country="test2")

    def test_manufacturer_ordering(self):
        obj1 = Manufacturer.objects.create(name="B", country="test")
        obj2 = Manufacturer.objects.create(name="A", country="test")

        manufacturers = Manufacturer.objects.all()
        self.assertEqual(list(manufacturers), [obj2, obj1])

    def test_manufacturer_name_max_length(self):
        manufacturer = Manufacturer.objects.create(name="A" * 256, country="test")

        with self.assertRaises(ValidationError):
            manufacturer.full_clean()

    def test_driver_str(self):
        driver = get_user_model().objects.create_user(
            username="test",
            first_name="first test",
            last_name="last test",
            password="test123",
        )
        self.assertEqual(
            str(driver), f"{driver.username} ({driver.first_name} {driver.last_name})"
        )

    def test_driver_unique_lisence(self):
        get_user_model().objects.create(
            username="test", password="test123", license_number="test_license"
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                username="test 2", password="test123", license_number="test_license"
            )

    def test_driver_get_absolute_url(self):
        driver = get_user_model().objects.create_user(
            username="test", password="test123", license_number="ABC123"
        )
        self.assertEqual(driver.get_absolute_url(), f"/drivers/{driver.pk}/")

    def test_car_str(self):
        manufacturer = Manufacturer.objects.create(name="test", country="test")

        driver = get_user_model().objects.create_user(
            username="test",
            first_name="first test",
            last_name="last test",
            password="test123",
        )

        car = Car.objects.create(
            model="test",
            manufacturer=manufacturer,
        )
        car.drivers.add(driver)

        self.assertEqual(str(car), car.model)
        self.assertIn(car, driver.cars.all())

    def test_driver_verbose_name(self):
        self.assertEqual(Driver._meta.verbose_name, "driver")
        self.assertEqual(Driver._meta.verbose_name_plural, "drivers")

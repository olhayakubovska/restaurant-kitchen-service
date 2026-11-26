from django.test import TestCase

from kitchen.forms import CookCreationForm, DishForm
from kitchen.models import DishCategory


class CookCreationFormTests(TestCase):
    def test_creates_cook_with_hashed_password(self):
        form = CookCreationForm(
            data={
                "username": "iryna",
                "first_name": "Iryna",
                "last_name": "Bondar",
                "email": "iryna@example.com",
                "experience": 2,
                "password1": "Sup3r-secret-pass",
                "password2": "Sup3r-secret-pass",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        cook = form.save()
        self.assertEqual(cook.experience, 2)
        self.assertNotEqual(cook.password, "Sup3r-secret-pass")
        self.assertTrue(cook.check_password("Sup3r-secret-pass"))

    def test_rejects_mismatched_passwords(self):
        form = CookCreationForm(
            data={
                "username": "iryna",
                "experience": 1,
                "password1": "Sup3r-secret-pass",
                "password2": "another-pass-123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class DishFormTests(TestCase):
    def setUp(self):
        self.category = DishCategory.objects.create(name="Salads")

    def test_valid_form_saves_dish(self):
        form = DishForm(
            data={
                "name": "Greek salad",
                "price": "150.00",
                "description": "Fresh vegetables",
                "dish_category": self.category.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        dish = form.save()
        self.assertEqual(dish.dish_category, self.category)

    def test_negative_price_is_invalid(self):
        form = DishForm(
            data={
                "name": "Salad",
                "price": "-1",
                "dish_category": self.category.pk,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_zero_price_is_invalid(self):
        form = DishForm(
            data={
                "name": "Salad",
                "price": "0",
                "dish_category": self.category.pk,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

from decimal import Decimal

from django.db.models import ProtectedError
from django.test import TestCase

from kitchen.models import Cook, Dish, DishCategory, Ingredient


class ModelStrTests(TestCase):
    def test_dish_category_str(self):
        category = DishCategory.objects.create(name="Супи")
        self.assertEqual(str(category), "Супи")

    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(name="Томати")
        self.assertEqual(str(ingredient), "Томати")

    def test_cook_str_uses_full_name(self):
        cook = Cook.objects.create_user(
            username="taras", first_name="Тарас", last_name="Шевчук"
        )
        self.assertEqual(str(cook), "Тарас Шевчук")

    def test_cook_str_falls_back_to_username(self):
        cook = Cook.objects.create_user(username="taras")
        self.assertEqual(str(cook), "taras")

    def test_dish_str(self):
        category = DishCategory.objects.create(name="Супи")
        dish = Dish.objects.create(
            name="Борщ", price=Decimal("140.00"), dish_category=category
        )
        self.assertEqual(str(dish), "Борщ")


class DishRelationTests(TestCase):
    def setUp(self):
        self.category = DishCategory.objects.create(name="Паста")
        self.dish = Dish.objects.create(
            name="Карбонара", price=Decimal("245.00"), dish_category=self.category
        )

    def test_cooks_and_ingredients_are_reachable_from_both_sides(self):
        cook = Cook.objects.create_user(username="maria")
        bacon = Ingredient.objects.create(name="Бекон")
        self.dish.cooks.add(cook)
        self.dish.ingredients.add(bacon)

        self.assertIn(self.dish, cook.dishes.all())
        self.assertIn(self.dish, bacon.dishes.all())

    def test_category_with_dishes_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_deleting_ingredient_keeps_dish(self):
        bacon = Ingredient.objects.create(name="Бекон")
        self.dish.ingredients.add(bacon)
        bacon.delete()

        self.dish.refresh_from_db()
        self.assertEqual(self.dish.ingredients.count(), 0)

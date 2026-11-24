from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from kitchen.models import Cook, Dish, DishCategory, Ingredient

PROTECTED_URLS = [
    "kitchen:index",
    "kitchen:dish-list",
    "kitchen:dish-create",
    "kitchen:dish-category-list",
    "kitchen:cook-list",
    "kitchen:cook-create",
    "kitchen:ingredient-list",
]


class AnonymousAccessTests(TestCase):
    def test_pages_redirect_to_login(self):
        for name in PROTECTED_URLS:
            with self.subTest(url=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")


class LoggedInTestCase(TestCase):
    def setUp(self):
        self.user = Cook.objects.create_user(username="chef", password="test-pass-1")
        self.client.force_login(self.user)

        self.soups = DishCategory.objects.create(name="Супи")
        self.desserts = DishCategory.objects.create(name="Десерти")
        self.borscht = Dish.objects.create(
            name="Борщ", price=Decimal("140"), dish_category=self.soups
        )
        self.napoleon = Dish.objects.create(
            name="Наполеон", price=Decimal("120"), dish_category=self.desserts
        )


class PageRenderTests(LoggedInTestCase):
    def test_pages_render_for_logged_in_user(self):
        for name in PROTECTED_URLS:
            with self.subTest(url=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_index_shows_counters(self):
        response = self.client.get(reverse("kitchen:index"))
        self.assertEqual(response.context["num_dishes"], 2)
        self.assertEqual(response.context["num_categories"], 2)


class DishListTests(LoggedInTestCase):
    url = reverse("kitchen:dish-list")

    def test_search_by_name(self):
        response = self.client.get(self.url, {"name": "Бор"})
        self.assertEqual(list(response.context["dish_list"]), [self.borscht])

    def test_filter_by_category(self):
        response = self.client.get(self.url, {"category": self.desserts.pk})
        self.assertEqual(list(response.context["dish_list"]), [self.napoleon])

    def test_invalid_category_is_ignored(self):
        response = self.client.get(self.url, {"category": "abc"})
        self.assertEqual(len(response.context["dish_list"]), 2)

    def test_pagination(self):
        for i in range(12):
            Dish.objects.create(
                name=f"Страва {i}", price=Decimal("10"), dish_category=self.soups
            )
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["dish_list"]), 12)


class DishCrudTests(LoggedInTestCase):
    def test_create_dish(self):
        response = self.client.post(
            reverse("kitchen:dish-create"),
            {"name": "Вареники", "price": "125", "dish_category": self.soups.pk},
        )
        self.assertRedirects(response, reverse("kitchen:dish-list"))
        self.assertTrue(Dish.objects.filter(name="Вареники").exists())

    def test_update_dish(self):
        self.client.post(
            reverse("kitchen:dish-update", args=[self.borscht.pk]),
            {"name": "Борщ", "price": "150", "dish_category": self.soups.pk},
        )
        self.borscht.refresh_from_db()
        self.assertEqual(self.borscht.price, Decimal("150"))

    def test_delete_dish(self):
        self.client.post(reverse("kitchen:dish-delete", args=[self.borscht.pk]))
        self.assertFalse(Dish.objects.filter(pk=self.borscht.pk).exists())


class DishCategoryDeleteTests(LoggedInTestCase):
    def test_category_with_dishes_is_not_deleted(self):
        response = self.client.post(
            reverse("kitchen:dish-category-delete", args=[self.soups.pk]),
            follow=True,
        )
        self.assertTrue(DishCategory.objects.filter(pk=self.soups.pk).exists())
        self.assertContains(response, "Неможливо видалити")

    def test_empty_category_is_deleted(self):
        empty = DishCategory.objects.create(name="Напої")
        self.client.post(reverse("kitchen:dish-category-delete", args=[empty.pk]))
        self.assertFalse(DishCategory.objects.filter(pk=empty.pk).exists())


class CookAndIngredientTests(LoggedInTestCase):
    def test_cook_search_by_username(self):
        Cook.objects.create_user(username="maria")
        response = self.client.get(reverse("kitchen:cook-list"), {"name": "mar"})
        self.assertEqual(
            [cook.username for cook in response.context["cook_list"]], ["maria"]
        )

    def test_ingredient_search(self):
        Ingredient.objects.create(name="Томати")
        Ingredient.objects.create(name="Бекон")
        response = self.client.get(reverse("kitchen:ingredient-list"), {"name": "Том"})
        self.assertEqual(
            [i.name for i in response.context["ingredient_list"]], ["Томати"]
        )

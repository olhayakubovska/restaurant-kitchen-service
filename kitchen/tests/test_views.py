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

        self.soups = DishCategory.objects.create(name="Soups")
        self.desserts = DishCategory.objects.create(name="Desserts")
        self.borscht = Dish.objects.create(
            name="Borscht", price=Decimal("140"), dish_category=self.soups
        )
        self.napoleon = Dish.objects.create(
            name="Napoleon", price=Decimal("120"), dish_category=self.desserts
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
        response = self.client.get(self.url, {"name": "Bor"})
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
                name=f"Dish {i}", price=Decimal("10"), dish_category=self.soups
            )
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["dish_list"]), 12)


class DishCrudTests(LoggedInTestCase):
    def test_create_dish(self):
        response = self.client.post(
            reverse("kitchen:dish-create"),
            {"name": "Varenyky", "price": "125", "dish_category": self.soups.pk},
        )
        dish = Dish.objects.get(name="Varenyky")
        self.assertRedirects(
            response, reverse("kitchen:dish-ingredients", args=[dish.pk])
        )

    def test_update_dish(self):
        self.client.post(
            reverse("kitchen:dish-update", args=[self.borscht.pk]),
            {"name": "Borscht", "price": "150", "dish_category": self.soups.pk},
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
        self.assertContains(response, "Cannot delete")

    def test_empty_category_is_deleted(self):
        empty = DishCategory.objects.create(name="Drinks")
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
        Ingredient.objects.create(name="Tomatoes")
        Ingredient.objects.create(name="Bacon")
        response = self.client.get(reverse("kitchen:ingredient-list"), {"name": "Tom"})
        self.assertEqual(
            [i.name for i in response.context["ingredient_list"]], ["Tomatoes"]
        )


class CookCrudTests(LoggedInTestCase):
    def setUp(self):
        super().setUp()
        self.cook = Cook.objects.create_user(
            username="cook7", first_name="Maria", last_name="Vovk"
        )

    def test_cook_search_by_first_name(self):
        response = self.client.get(reverse("kitchen:cook-list"), {"name": "mari"})
        self.assertEqual(list(response.context["cook_list"]), [self.cook])

    def test_cook_search_by_last_name(self):
        response = self.client.get(reverse("kitchen:cook-list"), {"name": "vovk"})
        self.assertEqual(list(response.context["cook_list"]), [self.cook])

    def test_update_cook(self):
        response = self.client.post(
            reverse("kitchen:cook-update", args=[self.cook.pk]),
            {"username": "cook7", "first_name": "Maria", "experience": "7"},
        )
        self.assertRedirects(response, reverse("kitchen:cook-list"))
        self.cook.refresh_from_db()
        self.assertEqual(self.cook.experience, 7)

    def test_delete_cook(self):
        self.client.post(reverse("kitchen:cook-delete", args=[self.cook.pk]))
        self.assertFalse(Cook.objects.filter(pk=self.cook.pk).exists())

    def test_cannot_delete_own_account(self):
        response = self.client.post(
            reverse("kitchen:cook-delete", args=[self.user.pk]), follow=True
        )
        self.assertTrue(Cook.objects.filter(pk=self.user.pk).exists())
        self.assertContains(response, "You cannot delete your own account.")


class DishRelationTests(LoggedInTestCase):
    def setUp(self):
        super().setUp()
        self.tomatoes = Ingredient.objects.create(name="Tomatoes")
        self.bacon = Ingredient.objects.create(name="Bacon")

    def test_ingredients_page_search(self):
        response = self.client.get(
            reverse("kitchen:dish-ingredients", args=[self.borscht.pk]),
            {"name": "tom"},
        )
        self.assertEqual(list(response.context["ingredient_list"]), [self.tomatoes])

    def test_ingredients_page_is_paginated(self):
        for i in range(12):
            Ingredient.objects.create(name=f"Spice {i}")
        response = self.client.get(
            reverse("kitchen:dish-ingredients", args=[self.borscht.pk])
        )
        self.assertEqual(len(response.context["ingredient_list"]), 10)

    def test_add_and_remove_ingredient(self):
        add_url = reverse(
            "kitchen:dish-ingredient-add", args=[self.borscht.pk, self.tomatoes.pk]
        )
        response = self.client.post(add_url + "?name=tom&page=1")
        self.assertRedirects(
            response,
            reverse("kitchen:dish-ingredients", args=[self.borscht.pk])
            + "?name=tom&page=1",
        )
        self.assertIn(self.tomatoes, self.borscht.ingredients.all())

        self.client.post(
            reverse(
                "kitchen:dish-ingredient-remove",
                args=[self.borscht.pk, self.tomatoes.pk],
            )
        )
        self.assertNotIn(self.tomatoes, self.borscht.ingredients.all())

    def test_add_and_remove_cook(self):
        cook = Cook.objects.create_user(username="anna")
        self.client.post(
            reverse("kitchen:dish-cook-add", args=[self.borscht.pk, cook.pk])
        )
        self.assertIn(cook, self.borscht.cooks.all())

        self.client.post(
            reverse("kitchen:dish-cook-remove", args=[self.borscht.pk, cook.pk])
        )
        self.assertNotIn(cook, self.borscht.cooks.all())

    def test_get_does_not_change_dish(self):
        response = self.client.get(
            reverse(
                "kitchen:dish-ingredient-add", args=[self.borscht.pk, self.bacon.pk]
            )
        )
        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.borscht.ingredients.exists())

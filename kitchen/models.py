from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class DishCategory(models.Model):
    name = models.CharField("Category name", max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "dish category"
        verbose_name_plural = "dish categories"

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Ingredient name", max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"

    def __str__(self) -> str:
        return self.name


class Cook(AbstractUser):
    experience = models.PositiveIntegerField("Experience, years", default=0)
    photo = models.ImageField("Photo", upload_to="cooks/", blank=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "cook"
        verbose_name_plural = "cooks"

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class Dish(models.Model):
    name = models.CharField("Dish name", max_length=255, unique=True)
    image = models.ImageField("Dish photo", upload_to="dishes/", blank=True)
    description = models.TextField("Description", blank=True, max_length=500)
    price = models.DecimalField(
        "Price, UAH",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    dish_category = models.ForeignKey(
        DishCategory,
        on_delete=models.PROTECT,
        related_name="dishes",
        verbose_name="Category",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="dishes",
        blank=True,
        verbose_name="Ingredients",
    )
    cooks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="dishes",
        blank=True,
        verbose_name="Responsible cooks",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "dish"
        verbose_name_plural = "dishes"

    def __str__(self) -> str:
        return self.name

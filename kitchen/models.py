from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models


class DishCategory(models.Model):
    name = models.CharField("Назва категорії", max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "категорія страв"
        verbose_name_plural = "категорії страв"

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Назва інгредієнта", max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "інгредієнт"
        verbose_name_plural = "інгредієнти"

    def __str__(self) -> str:
        return self.name


class Cook(AbstractUser):
    experience = models.PositiveIntegerField("Досвід, років", default=0)
    photo = models.ImageField("Фото", upload_to="cooks/", blank=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "кухар"
        verbose_name_plural = "кухарі"

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class Dish(models.Model):
    name = models.CharField("Назва страви", max_length=255, unique=True)
    image = models.ImageField("Фото страви", upload_to="dishes/", blank=True)
    description = models.TextField(
        "Опис",
        blank=True,
        validators=[MaxLengthValidator(500)],
    )
    price = models.DecimalField(
        "Ціна, грн",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    dish_category = models.ForeignKey(
        DishCategory,
        on_delete=models.PROTECT,
        related_name="dishes",
        verbose_name="Категорія",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="dishes",
        blank=True,
        verbose_name="Інгредієнти",
    )
    cooks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="dishes",
        blank=True,
        verbose_name="Відповідальні кухарі",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "страва"
        verbose_name_plural = "страви"

    def __str__(self) -> str:
        return self.name

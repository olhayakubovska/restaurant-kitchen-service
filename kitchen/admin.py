from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from kitchen.models import Cook, Dish, DishCategory, Ingredient


@admin.register(Cook)
class CookAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("experience",)
    fieldsets = UserAdmin.fieldsets + (("Кухня", {"fields": ("experience", "photo")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Кухня", {"fields": ("first_name", "last_name", "experience")}),
    )


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "dish_category", "price")
    list_filter = ("dish_category",)
    search_fields = ("name",)
    filter_horizontal = ("cooks", "ingredients")


@admin.register(DishCategory)
class DishCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)

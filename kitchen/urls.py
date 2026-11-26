from django.urls import path

from kitchen.models import Cook, Ingredient
from kitchen.views import (
    CookCreateView,
    CookDeleteView,
    CookListView,
    CookUpdateView,
    DishCategoryCreateView,
    DishCategoryDeleteView,
    DishCategoryListView,
    DishCategoryUpdateView,
    DishCreateView,
    DishDeleteView,
    DishCooksView,
    DishIngredientsView,
    DishListView,
    DishRelationChangeView,
    DishUpdateView,
    IndexView,
    IngredientCreateView,
    IngredientDeleteView,
    IngredientListView,
    IngredientUpdateView,
)

app_name = "kitchen"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dishes/", DishListView.as_view(), name="dish-list"),
    path("dishes/create/", DishCreateView.as_view(), name="dish-create"),
    path("dishes/<int:pk>/update/", DishUpdateView.as_view(), name="dish-update"),
    path("dishes/<int:pk>/delete/", DishDeleteView.as_view(), name="dish-delete"),
    path(
        "dishes/<int:pk>/ingredients/",
        DishIngredientsView.as_view(),
        name="dish-ingredients",
    ),
    path(
        "dishes/<int:pk>/ingredients/<int:item_pk>/add/",
        DishRelationChangeView.as_view(
            relation="ingredients",
            item_model=Ingredient,
            url_name="kitchen:dish-ingredients",
        ),
        name="dish-ingredient-add",
    ),
    path(
        "dishes/<int:pk>/ingredients/<int:item_pk>/remove/",
        DishRelationChangeView.as_view(
            relation="ingredients",
            item_model=Ingredient,
            url_name="kitchen:dish-ingredients",
            remove=True,
        ),
        name="dish-ingredient-remove",
    ),
    path("dishes/<int:pk>/cooks/", DishCooksView.as_view(), name="dish-cooks"),
    path(
        "dishes/<int:pk>/cooks/<int:item_pk>/add/",
        DishRelationChangeView.as_view(
            relation="cooks",
            item_model=Cook,
            url_name="kitchen:dish-cooks",
        ),
        name="dish-cook-add",
    ),
    path(
        "dishes/<int:pk>/cooks/<int:item_pk>/remove/",
        DishRelationChangeView.as_view(
            relation="cooks",
            item_model=Cook,
            url_name="kitchen:dish-cooks",
            remove=True,
        ),
        name="dish-cook-remove",
    ),
    path(
        "dish-categories/",
        DishCategoryListView.as_view(),
        name="dish-category-list",
    ),
    path(
        "dish-categories/create/",
        DishCategoryCreateView.as_view(),
        name="dish-category-create",
    ),
    path(
        "dish-categories/<int:pk>/update/",
        DishCategoryUpdateView.as_view(),
        name="dish-category-update",
    ),
    path(
        "dish-categories/<int:pk>/delete/",
        DishCategoryDeleteView.as_view(),
        name="dish-category-delete",
    ),
    path("cooks/", CookListView.as_view(), name="cook-list"),
    path("cooks/create/", CookCreateView.as_view(), name="cook-create"),
    path("cooks/<int:pk>/update/", CookUpdateView.as_view(), name="cook-update"),
    path("cooks/<int:pk>/delete/", CookDeleteView.as_view(), name="cook-delete"),
    path("ingredients/", IngredientListView.as_view(), name="ingredient-list"),
    path(
        "ingredients/create/",
        IngredientCreateView.as_view(),
        name="ingredient-create",
    ),
    path(
        "ingredients/<int:pk>/update/",
        IngredientUpdateView.as_view(),
        name="ingredient-update",
    ),
    path(
        "ingredients/<int:pk>/delete/",
        IngredientDeleteView.as_view(),
        name="ingredient-delete",
    ),
]

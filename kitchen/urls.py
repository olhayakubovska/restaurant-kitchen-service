from django.urls import path

from kitchen.views import (
    CookCreateView,
    CookListView,
    DishCategoryCreateView,
    DishCategoryDeleteView,
    DishCategoryListView,
    DishCategoryUpdateView,
    DishCreateView,
    DishDeleteView,
    DishListView,
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

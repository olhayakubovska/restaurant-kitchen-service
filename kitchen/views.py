from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from kitchen.forms import CookCreationForm, DishForm
from kitchen.mixins import SearchMixin
from kitchen.models import Cook, Dish, DishCategory, Ingredient


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = "kitchen/index.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["num_dishes"] = Dish.objects.count()
        context["num_categories"] = DishCategory.objects.count()
        context["num_cooks"] = Cook.objects.count()
        context["num_ingredients"] = Ingredient.objects.count()
        context["latest_dishes"] = (
            Dish.objects.select_related("dish_category")
            .prefetch_related("cooks")
            .order_by("-id")[:6]
        )
        context["cooks"] = Cook.objects.annotate(num_dishes=Count("dishes")).order_by(
            "-experience"
        )[:6]
        context["categories"] = DishCategory.objects.annotate(
            num_dishes=Count("dishes")
        ).order_by("-num_dishes", "name")
        return context


class DishListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Dish
    queryset = Dish.objects.select_related("dish_category").prefetch_related(
        "cooks", "ingredients"
    )
    search_field = "name"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get("category", "")
        if category.isdigit():
            queryset = queryset.filter(dish_category_id=category)
        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["categories"] = DishCategory.objects.all()
        context["active_category"] = self.request.GET.get("category", "")
        return context


class DishCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")
    success_message = "Страву «%(name)s» створено."


class DishUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")
    success_message = "Страву «%(name)s» збережено."


class DishDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Dish
    success_url = reverse_lazy("kitchen:dish-list")
    success_message = "Страву видалено."


class DishCategoryListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = DishCategory
    queryset = DishCategory.objects.prefetch_related("dishes")
    search_field = "name"
    paginate_by = 12


class DishCategoryCreateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.CreateView
):
    model = DishCategory
    fields = ("name",)
    success_url = reverse_lazy("kitchen:dish-category-list")
    success_message = "Категорію «%(name)s» створено."


class DishCategoryUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView
):
    model = DishCategory
    fields = ("name",)
    success_url = reverse_lazy("kitchen:dish-category-list")
    success_message = "Категорію «%(name)s» збережено."


class DishCategoryDeleteView(
    LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView
):
    model = DishCategory
    success_url = reverse_lazy("kitchen:dish-category-list")
    success_message = "Категорію видалено."

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f"Неможливо видалити «{self.object.name}»: у категорії є страви.",
            )
            return redirect("kitchen:dish-category-list")


class CookListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Cook
    queryset = Cook.objects.prefetch_related("dishes")
    search_field = "username"
    paginate_by = 12


class CookCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Cook
    form_class = CookCreationForm
    success_url = reverse_lazy("kitchen:cook-list")
    success_message = "Кухаря «%(username)s» додано до команди."


class IngredientListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Ingredient
    queryset = Ingredient.objects.prefetch_related("dishes")
    search_field = "name"
    paginate_by = 10


class IngredientCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Ingredient
    fields = ("name",)
    success_url = reverse_lazy("kitchen:ingredient-list")
    success_message = "Інгредієнт «%(name)s» додано."


class IngredientUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Ingredient
    fields = ("name",)
    success_url = reverse_lazy("kitchen:ingredient-list")
    success_message = "Інгредієнт «%(name)s» збережено."


class IngredientDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Ingredient
    success_url = reverse_lazy("kitchen:ingredient-list")
    success_message = "Інгредієнт видалено."

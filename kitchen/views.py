from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from kitchen.forms import CookCreationForm, CookUpdateForm, DishForm
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
    search_fields = ("name",)
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
    success_message = "Dish “%(name)s” was created. Now add its ingredients."

    def get_success_url(self) -> str:
        return reverse("kitchen:dish-ingredients", args=[self.object.pk])


class DishUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")
    success_message = "Dish “%(name)s” was saved."


class DishDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Dish
    success_url = reverse_lazy("kitchen:dish-list")
    success_message = "Dish was deleted."


class DishIngredientsView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Ingredient
    template_name = "kitchen/dish_ingredients.html"
    search_fields = ("name",)
    paginate_by = 10

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        dish = get_object_or_404(Dish, pk=self.kwargs["pk"])
        context["dish"] = dish
        context["selected"] = dish.ingredients.all()
        return context


class DishCooksView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Cook
    template_name = "kitchen/dish_cooks.html"
    search_fields = ("username", "first_name", "last_name")
    paginate_by = 10

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        dish = get_object_or_404(Dish, pk=self.kwargs["pk"])
        context["dish"] = dish
        context["selected"] = dish.cooks.all()
        return context


class DishRelationChangeView(LoginRequiredMixin, generic.View):
    relation = ""
    item_model = None
    url_name = ""
    remove = False

    def post(self, request, pk, item_pk):
        dish = get_object_or_404(Dish, pk=pk)
        item = get_object_or_404(self.item_model, pk=item_pk)
        related = getattr(dish, self.relation)

        if self.remove:
            related.remove(item)
        else:
            related.add(item)

        url = reverse(self.url_name, args=[dish.pk])
        if request.GET:
            url += "?" + request.GET.urlencode()
        return redirect(url)


class DishCategoryListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = DishCategory
    queryset = DishCategory.objects.prefetch_related("dishes")
    search_fields = ("name",)
    paginate_by = 12


class DishCategoryCreateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.CreateView
):
    model = DishCategory
    fields = ("name",)
    success_url = reverse_lazy("kitchen:dish-category-list")
    success_message = "Category “%(name)s” was created."


class DishCategoryUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView
):
    model = DishCategory
    fields = ("name",)
    success_url = reverse_lazy("kitchen:dish-category-list")
    success_message = "Category “%(name)s” was saved."


class DishCategoryDeleteView(
    LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView
):
    model = DishCategory
    success_url = reverse_lazy("kitchen:dish-category-list")
    success_message = "Category was deleted."

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f"Cannot delete “{self.object.name}”: the category still has dishes.",
            )
            return redirect("kitchen:dish-category-list")


class CookListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Cook
    queryset = Cook.objects.prefetch_related("dishes")
    search_fields = ("username", "first_name", "last_name")
    paginate_by = 12


class CookCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Cook
    form_class = CookCreationForm
    success_url = reverse_lazy("kitchen:cook-list")
    success_message = "Cook “%(username)s” was added to the team."


class CookUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Cook
    form_class = CookUpdateForm
    success_url = reverse_lazy("kitchen:cook-list")
    success_message = "Cook “%(username)s” was saved."


class CookDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Cook
    success_url = reverse_lazy("kitchen:cook-list")
    success_message = "Cook was removed from the team."

    def form_valid(self, form):
        if self.object == self.request.user:
            messages.error(self.request, "You cannot delete your own account.")
            return redirect("kitchen:cook-list")
        return super().form_valid(form)


class IngredientListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Ingredient
    queryset = Ingredient.objects.prefetch_related("dishes")
    search_fields = ("name",)
    paginate_by = 10


class IngredientCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Ingredient
    fields = ("name",)
    success_url = reverse_lazy("kitchen:ingredient-list")
    success_message = "Ingredient “%(name)s” was added."


class IngredientUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Ingredient
    fields = ("name",)
    success_url = reverse_lazy("kitchen:ingredient-list")
    success_message = "Ingredient “%(name)s” was saved."


class IngredientDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Ingredient
    success_url = reverse_lazy("kitchen:ingredient-list")
    success_message = "Ingredient was deleted."

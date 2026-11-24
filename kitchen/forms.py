from django import forms
from django.contrib.auth.forms import UserCreationForm

from kitchen.models import Cook, Dish


class CookCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Cook
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "experience",
            "photo",
        )


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = (
            "name",
            "image",
            "price",
            "description",
            "dish_category",
            "cooks",
            "ingredients",
        )
        widgets = {
            "cooks": forms.CheckboxSelectMultiple,
            "ingredients": forms.CheckboxSelectMultiple,
        }


class SearchForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)

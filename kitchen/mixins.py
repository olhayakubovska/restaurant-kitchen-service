from django.db.models import QuerySet
from django.http import HttpRequest

from kitchen.forms import SearchForm


class SearchMixin:
    request: HttpRequest
    search_field: str | None = None
    search_param = "name"

    def get_search_value(self) -> str:
        return self.request.GET.get(self.search_param, "").strip()

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        value = self.get_search_value()

        if value and self.search_field:
            queryset = queryset.filter(**{f"{self.search_field}__icontains": value})

        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(
            initial={self.search_param: self.get_search_value()}
        )
        return context

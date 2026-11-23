from typing import ClassVar

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model
from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin

User = get_user_model()


def test_htmx(request):
    print(request.htmx)


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "account/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class UserFieldInlineView(LoginRequiredMixin, SingleObjectMixin, View):
    model = User
    template_name = "account/profile.html"
    mode = "display"

    object: Model | None
    field_name: str | None

    editable_fields: ClassVar[dict[str, str]] = {
        "display_name": "Display Name",
        "username": "Username",
        "email": "Email",
    }

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.field_name = kwargs.get("field_name")

        if self.field_name is None or self.field_name not in self.editable_fields:
            raise Http404("Field cannot be edited.")

    def get_queryset(self):
        return super().get_queryset().filter(pk=self.request.user.pk)

    def get_field_context(self):
        if self.object is None:
            raise RuntimeError("Object has not been initialized.")

        if self.field_name is None:
            raise ValueError("Field name is required.")

        return {
            "object": self.object,
            "field_name": self.field_name,
            "field_label": self.editable_fields[self.field_name],
            "field_value": getattr(self.object, self.field_name),
        }

    def render_partial(self, partial_name):
        return render(
            self.request,
            f"{self.template_name}#{partial_name}",
            self.get_field_context(),
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        partial = "field-form" if self.mode == "edit" else "field-display"
        return self.render_partial(partial)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        new_value = request.POST.get("value", "").strip()

        if self.field_name is None:
            raise ValueError("Field name is required.")

        setattr(self.object, self.field_name, new_value)
        self.object.save(update_fields=[self.field_name])

        return self.render_partial("field-display")

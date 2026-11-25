from typing import ClassVar, cast

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Model
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from accounts.mixins import get_field_name
from accounts.models import User
from accounts.selectors import get_user_list


def test_htmx(request):
    print(request.htmx)


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "account/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class UserFieldView(LoginRequiredMixin, DetailView):
    """
    Get the htmx-get request with object pk and field_name,
    make sure user is authenticated to view the field,
    make sure user can only view it's own field,
    send response with field_name, field_value and object.
    """

    model = User
    template_name = "account/profile.html"

    object: Model

    def get_queryset(self):
        return super().get_queryset().filter(pk=self.request.user.pk)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        field_name = self.kwargs.get("field_name")
        context["field_name"] = field_name
        context["field_value"] = getattr(self.object, field_name)
        return context

    def get_template_names(self):
        return (f"{self.template_name}#field-display",)


class UserFieldInputView(LoginRequiredMixin, DetailView):
    """
    Get htmx-get request, validate the user login,
    check if the required fields belongs to the user,
    make sure user is not allowed to change other user's field,
    make sure the required image is allowed to be changed,
    then send the response with the partial input field with that field_name and field_value.
    """

    model = User
    template_name = "account/profile.html"

    object: Model

    ALLOWED_FIELDS: ClassVar[set[str]] = {
        "first_name",
        "last_name",
        "display_name",
        "username",
        "email",
    }

    def get_queryset(self):
        return super().get_queryset().filter(pk=self.request.user.pk)

    def get_template_names(self):
        return (f"{self.template_name}#field-form",)

    def get_field_name(self):
        field_name = self.kwargs.get("field_name")
        if field_name is None or field_name not in self.ALLOWED_FIELDS:
            raise Http404("Field cannot be edited.")
        return field_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        field_name = self.get_field_name()
        context["field_name"] = field_name
        context["field_value"] = getattr(self.object, field_name)
        return context


class UserFieldUpdateView(LoginRequiredMixin, SingleObjectMixin, View):
    """
    Get htmx post request with field_name, value and object,
    make sure user is authenticated and object belongs to the user,
    make sure field is allowed to change,
    update the field and save to database,
    send a response back with a partial template to the user.
    """

    model = User
    template_name = "account/profile.html"

    ALLOWED_FIELDS: ClassVar[set[str]] = {
        "first_name",
        "last_name",
        "display_name",
        "username",
        "email",
    }

    object: User

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        data = get_user_list(qs, user)
        return data

    def get_partial_template(self):
        is_active_field = self.kwargs.get("field_name", "") == "is_active"

        partial_template = {
            "display": f"{self.template_name}#field-display",
            "edit": f"{self.template_name}#field-form",
        }

        if is_active_field:
            partial_template["display"] = (
                "account/partials/user_partials.html#user_is_active"
            )
            partial_template["edit"] = (
                "account/partials/user_partials.html#user_is_active"
            )

        return partial_template

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        field_name = get_field_name(
            field_name=self.kwargs.get("field_name"),
            user=cast(User, self.request.user),
            target=self.object,
        )
        context["field_name"] = field_name
        context["field_value"] = getattr(self.object, field_name)
        return context

    def post(self, request, *args, **kwargs):
        self.object = cast(User, self.get_object())
        field_name = get_field_name(
            field_name=self.kwargs.get("field_name"),
            user=cast(User, self.request.user),
            target=self.object,
        )

        form_class = modelform_factory(
            self.model,
            fields=[field_name],
        )
        form_data = {
            field_name: request.POST.get("value", ""),
        }

        form = form_class(data=form_data, instance=self.object)

        if not form.is_valid():
            context = self.get_context_data()
            context["form"] = form

            return render(
                request,
                self.get_partial_template()["edit"],
                context,
            )

        self.object = form.save(commit=False)
        self.object.save(update_fields=[field_name])
        return render(
            self.request,
            self.get_partial_template()["display"],
            self.get_context_data(),
        )


class UserFieldInlineView(
    LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, View
):
    model = User
    template_name = "account/profile.html"
    mode = "display"

    object: Model | None
    field_name: str | None

    editable_fields: ClassVar[set[str]] = {"display_name", "username", "email"}

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
            "field_name": self.field_name,
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


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "account/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        data = get_user_list(qs, user)
        return data

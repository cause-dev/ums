from django.urls import path

from .views import (
    ProfileView,
    UserFieldInlineView,
    UserFieldInputView,
    UserFieldView,
    test_htmx,
)

urlpatterns = [
    path("test-htmx/", test_htmx, name="test_htmx"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "profile/<int:pk>/field/<str:field_name>/input/",
        UserFieldInputView.as_view(),
        name="user_input_field",
    ),
    path(
        "profile/<int:pk>/field/<str:field_name>/view/",
        UserFieldView.as_view(),
        name="user_view_field",
    ),
    path(
        "profile/<int:pk>/field/<str:field_name>/edit/",
        UserFieldInlineView.as_view(mode="edit"),
        name="user-field-edit",
    ),
    path(
        "profile/<int:pk>/field/<str:field_name>/",
        UserFieldInlineView.as_view(mode="display"),
        name="user-field",
    ),
]

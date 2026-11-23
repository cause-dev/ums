from django.urls import path

from .views import ProfileView, UserFieldInlineView, test_htmx

urlpatterns = [
    path("test-htmx/", test_htmx, name="test_htmx"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "profile/<int:pk>/field/<str:field_name>/",
        UserFieldInlineView.as_view(mode="edit"),
        name="user-field-edit",
    ),
    path(
        "profile/<int:pk>/field/<str:field_name>/",
        UserFieldInlineView.as_view(mode="display"),
        name="user-field",
    ),
]

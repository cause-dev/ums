from django.urls import path

from .views import (
    PermissionDeniedView,
    ProfileView,
    UserFieldInputView,
    UserFieldUpdateView,
    UserFieldView,
    UserListView,
)

urlpatterns = [
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
        UserFieldUpdateView.as_view(),
        name="user_update_field",
    ),
    path("users/", UserListView.as_view(), name="user_list"),
    path(
        "403/",
        PermissionDeniedView.as_view(),
        name="four_zero_three",
    ),
]

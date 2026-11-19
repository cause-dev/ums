from django.urls import path

from .views import test_htmx

urlpatterns = [
    path("test-htmx/", test_htmx, name="test_htmx"),
]

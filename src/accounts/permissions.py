import functools

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect

from accounts.constants import DEFAULT_ROLE_NAMES
from accounts.models import User


def has_role(user: User | AnonymousUser, role: str) -> bool:
    if not user.is_authenticated:
        return False

    if role not in DEFAULT_ROLE_NAMES:
        return False

    return user.groups.filter(name=role).exists()


def role_required(role: str):
    if role not in DEFAULT_ROLE_NAMES:
        raise ValueError("Please use a valid role.")

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return not_authenticated_response(request)
            if not has_role(request.user, role):
                return permission_denied_response(request)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def permission_denied_response(request):
    if not request.htmx:
        return render(request, "account/403.html", status=403)
    else:
        url = reverse("four_zero_three")
        return HttpResponseClientRedirect(redirect_to=url)


def not_authenticated_response(request):
    if not request.htmx:
        return redirect_to_login(request.get_full_path())
    else:
        current_url = request.headers.get("HX-Current-URL") or request.get_full_path()
        login_redirect = redirect_to_login(next=current_url)
        return HttpResponseClientRedirect(redirect_to=login_redirect.url)

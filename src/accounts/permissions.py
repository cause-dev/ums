import functools

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

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
                return redirect_to_login(request.get_full_path())
            if not has_role(request.user, role):
                raise PermissionDenied("You don't have permission to access this page!")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

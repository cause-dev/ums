# User Management System (UMS) with Django

## Setup custom user management on a Django project

1. Clone the repository:
```
git clone git@github.com:cause-dev/ums.git
```

2. Create a virtual environment and install dependencies:
```
uv sync
```

3. Add `accounts` to `INSTALLED_APPS` in `settings.py`.
4. Add `AUTH_USER_MODEL = "accounts.User"` to `settings.py`.
5. Run `python manage.py makemigrations` and `python manage.py migrate` to create the user model.

## Authentication

`django-allauth` is being used for authentication.
Follow the official [documentation](https://docs.allauth.org/en/latest/installation/quickstart.html) to set it up.

1. Install `django-allauth` using uv:
```
uv add django-allauth
```

2. Make sure `django.template.context_processors.request` is included in `TEMPLATES` context processors in `settings.py`.
3. Add `allauth.account.auth_backends.AuthenticationBackend` to `AUTHENTICATION_BACKENDS` in `settings.py`.
4. Add `allauth` and `allauth.account` to `INSTALLED_APPS` in `settings.py` after your custom user app.
5. Add `allauth.account.middleware.AccountMiddleware` to `MIDDLEWARE` in `settings.py`.
6. Include `path('accounts/', include('allauth.urls'))` in your project `urls.py`.
7. Run `python manage.py migrate` to apply the database migrations.
8. Force user to log in before accessing admin pages by adding:
```
from allauth.account.decorators import secure_admin_login
from django.contrib import admin

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)
```

## HTMX

`django_htmx` is a library that adds HTMX support to Django. You can follow the official [docs](https://django-htmx.readthedocs.io/en/latest/installation.html) to set it up.

1. Install `django_htmx` using uv:
```
uv add django_htmx
```

2. Add `django_htmx` to `INSTALLED_APPS` in `settings.py`.
3. Add `django_htmx.middleware.HtmxMiddleware` to `MIDDLEWARE` in `settings.py`.

## Role-based permissions

UMS uses Django's built-in `Group` model to manage application roles.

The following default roles are provided:

| Role    | Description                |
| ------- | -------------------------- |
| Admin   | Application administration |
| Manager | User management            |
| Editor  | Content management         |
| Viewer  | Read-only content access   |

Use the `role_required()` decorator from `accounts.permissions` to restrict access to views based on a user's role.

### Function-based views

```python
from accounts.permissions import role_required

@role_required("Admin")
def admin_dashboard(request):
    ...
```

### Class-based views

Use Django's `method_decorator` to apply `role_required()` to the `dispatch` method. This protects all HTTP methods, including GET and POST.

```python
from django.utils.decorators import method_decorator
from django.views import View

from accounts.permissions import role_required

@method_decorator(role_required("Admin"), name="dispatch")
class AdminDashboardView(View):
    ...
```

### Authentication and mixin ordering

When combining authentication and permission mixins in class-based views, always place authentication mixins before permission-related mixins in the inheritance list.

```python
class ProtectedView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    ...
```

Authentication mixins should run before permission checks to ensure unauthenticated users are handled correctly.

**Note:** `role_required()` already handles anonymous users, so an additional `LoginRequiredMixin` is not required solely for authentication when using this decorator.

### Permission-denied behavior

UMS handles normal HTTP and HTMX permission failures differently.

| Request                   | Behavior                                               |
| ------------------------- | ------------------------------------------------------ |
| Anonymous HTTP request    | Redirect to login                                      |
| Anonymous HTMX request    | Full-page redirect to login using `HX-Redirect`        |
| Unauthorized HTTP request | Render the 403 page with HTTP 403                      |
| Unauthorized HTMX request | Full-page redirect to the 403 page using `HX-Redirect` |

The HTMX permission handling requires `django_htmx.middleware.HtmxMiddleware` to be configured in the host project's `MIDDLEWARE` setting.

The `role_required()` decorator only accepts predefined application roles. Custom groups do not automatically qualify as application roles.

For example, a user belonging to the `Marketing` group does not automatically have the `Editor` role.

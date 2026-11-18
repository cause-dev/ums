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

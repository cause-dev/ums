from django.http import Http404

from accounts.models import User

ALLOWED_FIELDS: set[str] = {
    "first_name",
    "last_name",
    "display_name",
    "username",
    "email",
}

STAFF_ALLOWED_FIELDS: set[str] = {
    "is_active",
}


def get_field_name(field_name, user: User, target: User) -> str:
    """Validate field-level permissions for a user update.

    Regular users can edit their own allowed fields.
    Staff can edit their own allowed fields or change `is_active`
    for other regular users.

    Target accessibility (excluding other staff and superusers)
    must be enforced separately by the view's queryset.
    """

    if field_name is None:
        raise Http404("Field cannot be edited.")

    if field_name not in ALLOWED_FIELDS and field_name not in STAFF_ALLOWED_FIELDS:
        raise Http404("Field cannot be edited.")

    if user.is_staff and user.pk == target.pk and field_name not in ALLOWED_FIELDS:
        raise Http404("Field cannot be edited.")

    if (
        user.is_staff
        and user.pk != target.pk
        and field_name not in STAFF_ALLOWED_FIELDS
    ):
        raise Http404("Field cannot be edited.")

    if not user.is_staff and field_name not in ALLOWED_FIELDS:
        raise Http404("Field cannot be edited.")

    return field_name

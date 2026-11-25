from django.db.models import Q


def get_user_list(queryset, user):
    """Return the users accessible to the requesting user.

    Regular users can access only their own account.
    Staff can access their own account and regular users,
    but not other staff members or superusers.

    Returns a lazy QuerySet suitable for both list and
    single-object views.
    """
    if user.is_staff:
        return queryset.filter(Q(pk=user.pk) | Q(is_staff=False, is_superuser=False))

    return queryset.filter(pk=user.pk)

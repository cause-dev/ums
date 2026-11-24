from django.http import Http404


def get_user_list(queryset, user):
    if user.is_staff:
        return queryset.filter(is_staff=False, is_superuser=False)
    else:
        raise Http404("Only staff can access this information!")

from django.http import HttpResponse
from django.shortcuts import redirect, resolve_url


def hx_redirect(request, to, *args, **kwargs):
    """
    Redirects cleanly whether the request came from HTMX or a normal browser click.
    `to` can be a URL name ("dashboard"), a path ("/dashboard/"), or a model instance.
    """

    url = resolve_url(to, *args, **kwargs)

    if request.headers.get("HX-Request") == "true":
        response = HttpResponse()
        response["HX-Redirect"] = url
        return response

    return redirect(url)

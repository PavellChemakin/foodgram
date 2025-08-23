"""Custom pagination classes for the Foodgram API.

This module defines the pagination behaviour used throughout the
application.  The default ``PageNumberPagination`` provided by Django
REST framework does not allow the client to override the number of
objects returned on each page.  The front‑end bundled with Foodgram
expects to be able to specify a ``limit`` query parameter on most
collection endpoints (for example, ``/api/recipes/?page=1&limit=6``).

``CustomPagination`` adds support for a ``limit`` query parameter
whilst keeping a sensible default page size.  If the client does
not specify ``limit`` the paginator falls back to the value
configured on the class.  Setting ``page_size_query_param`` to
``limit`` instructs DRF to read this value from the querystring.

The default page size is six items to mirror the behaviour of the
reference implementation provided in the original Foodgram project.
"""

from __future__ import annotations

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Extend ``PageNumberPagination`` to support a ``limit`` parameter.

    The front‑end client uses ``limit`` to control how many objects
    should be returned in a single response.  By specifying
    ``page_size_query_param = 'limit'`` and setting a default
    ``page_size``, this paginator behaves identically to
    ``PageNumberPagination`` when no ``limit`` query parameter is
    supplied but allows the client to request a different page size
    when needed.  See ``DEFAULT_PAGINATION_CLASS`` in
    ``settings.py`` for how this class is used.
    """

    # name of the query parameter to control page size
    page_size_query_param: str = 'limit'
    # default number of items per page if ``limit`` is not supplied
    page_size: int = 6

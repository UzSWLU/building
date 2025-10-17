import threading
from typing import Optional
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

_thread_locals = threading.local()


def get_current_user():
    user = getattr(_thread_locals, 'user', None)
    return user if user and not isinstance(user, AnonymousUser) else None


class CurrentUserMiddleware:
    """Stores request.user in thread local so models can access current user.
    Add 'app_rttm.middleware.CurrentUserMiddleware' to MIDDLEWARE.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        _thread_locals.user = getattr(request, 'user', None)
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.user = None
        return response



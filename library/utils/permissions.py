from functools import wraps
from django.core.exceptions import PermissionDenied


def required_permissions(perms):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not all(request.user.has_perm(perm) for perm in perms):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

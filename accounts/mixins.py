from functools import wraps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin):
    """CBV mixin.

    Set `allowed_roles` to a list of group names.
    Optionally set `required_permission` (e.g. "appointments.add_appointment")
    so that users with NO group but with that individual Django permission
    are also granted access.  Group membership always takes priority.
    """
    allowed_roles: list = []
    required_permission: str = ""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self._has_role(request.user):
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def _has_role(self, user):
        if user.is_superuser:
            return True
        # Primary check: group membership
        if user.groups.filter(name__in=self.allowed_roles).exists():
            return True
        # Fallback: individual Django permission (for users without a group role)
        if self.required_permission and user.has_perm(self.required_permission):
            return True
        return False


def role_required(*roles, permission=None):
    """Function-view decorator.

    Usage: @role_required('Veterinario', 'Admin')
    With individual-perm fallback: @role_required('Veterinario', permission='medical.add_prescription')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.groups.filter(name__in=roles).exists():
                return view_func(request, *args, **kwargs)
            if permission and request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("dashboard")
        return _wrapped
    return decorator

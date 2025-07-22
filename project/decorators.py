from django.shortcuts import redirect
from functools import wraps

def is_project_manager_or_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['admin', 'manager']:
            return view_func(request, *args, **kwargs)
        return redirect('dashboard')
    return _wrapped_view

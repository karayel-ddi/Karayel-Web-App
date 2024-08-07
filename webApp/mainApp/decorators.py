from functools import wraps
from django.shortcuts import redirect

def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'admin_id' in request.session:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper
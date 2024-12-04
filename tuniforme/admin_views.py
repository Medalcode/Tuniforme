# tuniforme/admin_views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def admin_logout(request):
    logout(request)
    return redirect('/admin/login/')
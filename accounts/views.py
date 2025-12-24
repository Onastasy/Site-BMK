from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.urls import reverse

def login_view(request):
    next_url = request.GET.get("next") or reverse("profile")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.POST.get("next") or next_url)
        messages.error(request, "Неверный логин или пароль.")
    else:
        form = AuthenticationForm(request)
    return render(request, "accounts/login.html", {"form": form, "next_url": next_url})

def logout_view(request):
    logout(request)
    return redirect("home")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            g = Group.objects.filter(name="user").first()
            if g:
                user.groups.add(g)
            messages.success(request, "Аккаунт создан. Войдите на сайт.")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

@login_required
def profile(request):
    groups = ", ".join(g.name for g in request.user.groups.all()) or "—"
    role = "admin" if request.user.groups.filter(name="admin").exists() else "user"
    return render(request, "accounts/profile.html", {"groups": groups, "role": role})

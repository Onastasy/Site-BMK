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

@login_required
def dashboard(request):
    """Личный кабинет - главная страница"""
    # Получаем данные пользователя
    user_groups = ", ".join(g.name for g in request.user.groups.all()) or "—"
    role = "admin" if request.user.groups.filter(name="admin").exists() else "user"

    context = {
        "groups": user_groups,
        "role": role,
        "user": request.user,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def employee_list(request):
    """Список сотрудников компании"""
    from django.contrib.auth.models import User

    employees = User.objects.filter(is_active=True).order_by('last_name', 'first_name')

    # Добавляем информацию о группах для каждого сотрудника
    for emp in employees:
        emp.groups_list = ", ".join(g.name for g in emp.groups.all()) or "—"

    return render(request, "accounts/employee_list.html", {
        "employees": employees
    })


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя"""
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)

        # Если есть дополнительные поля в модели User или Profile
        if hasattr(user, 'profile'):
            user.profile.phone = request.POST.get("phone", getattr(user.profile, 'phone', ''))
            user.profile.department = request.POST.get("department", getattr(user.profile, 'department', ''))
            user.profile.position = request.POST.get("position", getattr(user.profile, 'position', ''))
            user.profile.save()

        user.save()
        messages.success(request, "Профиль успешно обновлён!")
        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {
        "user": request.user
    })


@login_required
def user_files(request):
    """Файлы пользователя (если ещё нет в messaging)"""
    # Здесь можно подключить модель FileAttachment из messaging
    # или оставить заглушку для будущей реализации
    return render(request, "accounts/files.html", {
        "files": []  # Замените на реальные данные из БД
    })
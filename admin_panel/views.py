from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


def is_admin(user):
    """Проверка, что пользователь - администратор"""
    return user.is_authenticated and user.groups.filter(name="admin").exists()


@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def dashboard(request):
    """Главная страница"""

    # Базовая статистика
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_groups': Group.objects.count(),
        'new_users_today': User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count(),
        'new_users_week': User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }

    # Получить статистику из других приложений
    try:
        from news.models import NewsPost
        stats['total_news'] = NewsPost.objects.count()
    except ImportError:
        stats['total_news'] = 0

    try:
        from messaging.models import Message
        stats['total_messages'] = Message.objects.count()
    except ImportError:
        stats['total_messages'] = 0

    # Последние зарегистрированные пользователи
    latest_users = User.objects.filter(is_active=True).order_by('-date_joined')[:10]

    context = {
        'stats': stats,
        'latest_users': latest_users,
        'title': 'Админ-панель',
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def users_list(request):
    """Управление пользователями"""
    users = User.objects.all().order_by('-date_joined')

    # Добавить информацию о группах
    for user in users:
        user.groups_list = ", ".join(g.name for g in user.groups.all()) or "—"
        user.is_admin = user.groups.filter(name="admin").exists()
        user.is_manager = user.groups.filter(name="manager").exists()

    context = {
        'users': users,
        'title': 'Управление пользователями',
    }
    return render(request, 'admin_panel/users_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def user_edit(request, user_id):
    """Редактирование пользователя"""
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Обновление основных данных
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.is_active = request.POST.get("is_active") == "on"

        # Обновление групп
        groups = request.POST.getlist("groups")
        user.groups.clear()
        for group_name in groups:
            group = Group.objects.filter(name=group_name).first()
            if group:
                user.groups.add(group)

        user.save()
        messages.success(request, f"Пользователь {user.username} обновлён!")
        return redirect("admin_panel:users_list")

    all_groups = Group.objects.all()
    user_groups = list(user.groups.values_list('name', flat=True))

    context = {
        'edit_user': user,
        'all_groups': all_groups,
        'user_groups': user_groups,
        'title': f'Редактирование: {user.username}',
    }
    return render(request, 'admin_panel/user_edit.html', context)


@login_required
@user_passes_test(is_admin, login_url='/accounts/login/')
def groups_list(request):
    """Управление группами/ролями"""
    groups = Group.objects.all().annotate(user_count=Count('user'))

    context = {
        'groups': groups,
        'title': 'Управление ролями',
    }
    return render(request, 'admin_panel/groups_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def news_management(request):
    """Управление новостями"""
    news_list = []
    try:
        from news.models import NewsPost
        news_list = NewsPost.objects.all().order_by('-created_at')
    except ImportError:
        messages.warning(request, "Приложение новостей не установлено")

    context = {
        'news_list': news_list,
        'title': 'Управление новостями',
    }
    return render(request, 'admin_panel/news_management.html', context)


@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def site_settings(request):
    """Настройки сайта"""
    from core.models import ContactInfo, Banner

    contact_info = ContactInfo.objects.first()
    banners = Banner.objects.all()

    context = {
        'contact_info': contact_info,
        'banners': banners,
        'title': 'Настройки сайта',
    }
    return render(request, 'admin_panel/site_settings.html', context)


@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def activity_log(request):
    """Журнал действий"""
    # Здесь можно создать модель ActivityLog и выводить действия пользователей
    context = {
        'title': 'Журнал действий',
        'activities': [],
    }
    return render(request, 'admin_panel/activity_log.html', context)

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from core.models import Banner, ContactInfo
from news.models import NewsPost

class Command(BaseCommand):
    help = "Create demo users, roles, banners, contacts, and a sample news post."

    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name="admin")
        user_group, _ = Group.objects.get_or_create(name="user")

        perms = Permission.objects.filter(codename__in=[
            "add_banner","change_banner","delete_banner",
            "add_contactinfo","change_contactinfo","delete_contactinfo",
            "add_newspost","change_newspost","delete_newspost",
            "add_message","change_message","delete_message",
        ])
        admin_group.permissions.set(perms)
        user_group.permissions.clear()

        if not User.objects.filter(username="admin").exists():
            u = User.objects.create_user("admin", password="admin123")
            u.is_staff = True
            u.save()
            u.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS("Created user admin/admin123"))

        if not User.objects.filter(username="user").exists():
            u = User.objects.create_user("user", password="user123")
            u.save()
            u.groups.add(user_group)
            self.stdout.write(self.style.SUCCESS("Created user user/user123"))

        ContactInfo.objects.get_or_create(org="Demo Org")
        if not Banner.objects.exists():
            Banner.objects.create(text="Добро пожаловать! Переключатель «Для слабовидящих» — в шапке.", href="/about/", enabled=True, order=1)
            Banner.objects.create(text="Новости проекта — в разделе «Новости».", href="/news/", enabled=True, order=2)

        if not NewsPost.objects.exists():
            author = User.objects.get(username="admin")
            NewsPost.objects.create(title="Запуск Django-версии", body="Добавлены новости, поиск, сообщения, баннеры, контакты и роли.", author=author)

        self.stdout.write(self.style.SUCCESS("Bootstrap complete."))

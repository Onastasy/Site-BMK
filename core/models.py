from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Banner(models.Model):
    text = models.CharField(max_length=255)
    href = models.CharField(max_length=255, default="/")
    enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["order", "id"]
    def __str__(self): return self.text

class ContactInfo(models.Model):
    org = models.CharField(max_length=255, default="Demo Org")
    phone = models.CharField(max_length=64, default="+7 (000) 000-00-00")
    email = models.EmailField(default="info@example.com")
    address = models.CharField(max_length=255, default="Россия, Москва, ул. Пример, 1")
    def __str__(self): return self.org

class Vacancy(models.Model):
    """Модель для страницы вакансий"""
    title = models.CharField(max_length=255, verbose_name='Название вакансии')
    department = models.CharField(max_length=100, verbose_name='Отдел')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(verbose_name='Требования')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Page(models.Model):
    """Модель для статических страниц"""
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='URL-адрес')
    content = models.TextField(verbose_name='Содержание')
    is_published = models.BooleanField(default=True, verbose_name='Опубликована')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.title


class UserActivity(models.Model):
    """Модель для отслеживания активности пользователей"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    action = models.CharField(max_length=255, verbose_name='Действие')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username} - {self.action}'
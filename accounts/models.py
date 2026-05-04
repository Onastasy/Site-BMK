from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""

    ONLINE = 'online'
    AWAY = 'away'
    BUSY = 'busy'
    OFFLINE = 'offline'

    STATUS_CHOICES = [
        (ONLINE, '🟢 В сети'),
        (AWAY, '🟡 Отошёл'),
        (BUSY, '🔴 Занят'),
        (OFFLINE, '⚫ Не в сети'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=ONLINE
    )
    bio = models.TextField('О себе', blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    department = models.CharField('Отдел', max_length=100, blank=True, null=True)
    position = models.CharField('Должность', max_length=100, blank=True, null=True)
    last_active = models.DateTimeField('Последняя активность', auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаёт профиль при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
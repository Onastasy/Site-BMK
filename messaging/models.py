from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """Личные сообщения между двумя пользователями"""
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.from_user}->{self.to_user})"

class ChatRoom(models.Model):
    """Групповые чаты и каналы"""

    class ChatType(models.TextChoices):
        PRIVATE = 'PRIVATE', 'Личная переписка'
        GROUP = 'GROUP', 'Групповой чат'
        CHANNEL = 'CHANNEL', 'Канал'
        SUPPORT = 'SUPPORT', 'Техподдержка'

    title = models.CharField('Название', max_length=200, blank=True, null=True)
    type = models.CharField(
        'Тип чата',
        max_length=20,
        choices=ChatType.choices,
        default=ChatType.GROUP
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_chats',
        verbose_name='Создатель'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    description = models.TextField('Описание', blank=True, null=True)
    avatar_url = models.TextField('Аватар (URL)', blank=True, null=True)
    is_archived = models.BooleanField('В архиве', default=False)

    # Последнее сообщение (для отображения в списке)
    last_message = models.ForeignKey(
        'ChatMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    def save(self, *args, **kwargs):
        """Автоматически генерирует заголовок для личных чатов без названия"""
        if self.type == self.ChatType.PRIVATE and not self.title:
            self.title = f'Личный чат #{self.pk or "новый"}'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Чат-комната'
        verbose_name_plural = 'Чат-комнаты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"


class ChatMembership(models.Model):
    """Участники чат-комнат"""

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Владелец'
        ADMIN = 'ADMIN', 'Администратор'
        MODERATOR = 'MODERATOR', 'Модератор'
        MEMBER = 'MEMBER', 'Участник'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_memberships',
        verbose_name='Пользователь'
    )
    chat = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Чат'
    )
    joined_at = models.DateTimeField('Дата вступления', auto_now_add=True)
    role_in_chat = models.CharField(
        'Роль в чате',
        max_length=50,
        choices=Role.choices,
        default=Role.MEMBER
    )
    is_muted = models.BooleanField('Уведомления выключены', default=False)
    nickname_in_chat = models.CharField(
        'Никнейм в чате',
        max_length=100,
        blank=True,
        null=True
    )
    last_read_message = models.ForeignKey(
        'ChatMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    left_at = models.DateTimeField('Дата выхода', null=True, blank=True)

    class Meta:
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чатов'
        unique_together = ['user', 'chat']

    def __str__(self):
        return f"{self.user.username} в {self.chat.title}"


class ChatMessage(models.Model):
    """Сообщения в групповых чатах"""

    chat = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Отправитель'
    )
    content = models.TextField('Текст сообщения', blank=True)
    sent_at = models.DateTimeField('Время отправки', auto_now_add=True, db_index=True)
    is_edited = models.BooleanField('Отредактировано', default=False)
    edited_at = models.DateTimeField('Дата редактирования', null=True, blank=True)
    is_deleted = models.BooleanField('Удалено', default=False)

    # Ответ на сообщение
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Ответ на'
    )

    # Кто прочитал
    read_by = models.ManyToManyField(
        User,
        related_name='read_chat_messages',
        blank=True,
        verbose_name='Прочитано'
    )

    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чатов'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['chat', 'sent_at']),
            models.Index(fields=['sender', 'sent_at']),
        ]

    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"Сообщение от {self.sender.username}: {preview}"


class MessageAttachment(models.Model):
    """Вложения к сообщениям чата"""

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Сообщение'
    )
    file_name = models.CharField('Имя файла', max_length=255)
    file_path = models.CharField('Путь к файлу', max_length=500)
    file_type = models.CharField('Тип файла', max_length=50)
    file_size = models.BigIntegerField('Размер (байты)', default=0)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    file_hash = models.CharField('Хеш файла', max_length=64, blank=True, null=True)
    download_count = models.IntegerField('Скачиваний', default=0)

    # Поле для реального файла
    file = models.FileField('Файл', upload_to='chat_attachments/%Y/%m/', null=True, blank=True)

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Файл {self.file_name} к сообщению #{self.message.id}"

    @property
    def is_image(self):
        """Проверка, является ли файл изображением"""
        return self.file_type.startswith('image/')

    @property
    def is_document(self):
        """Проверка, является ли файл документом"""
        doc_types = ['application/pdf', 'application/msword',
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'application/vnd.ms-excel',
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        return self.file_type in doc_types

    @property
    def is_archive(self):
        """Проверка, является ли файл архивом"""
        return self.file_type in ['application/zip', 'application/x-rar-compressed',
                                  'application/gzip', 'application/x-7z-compressed']

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Файл {self.file_name} к сообщению #{self.message.id}"


class ChatNotification(models.Model):
    """Уведомления чата"""

    class NotificationType(models.TextChoices):
        NEW_MESSAGE = 'NEW_MESSAGE', 'Новое сообщение'
        MENTION = 'MENTION', 'Упоминание'
        TICKET_UPDATE = 'TICKET_UPDATE', 'Обновление заявки'
        SYSTEM = 'SYSTEM', 'Системное'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_notifications',
        verbose_name='Пользователь'
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Сообщение'
    )
    type = models.CharField(
        'Тип',
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.NEW_MESSAGE
    )
    content = models.CharField('Текст уведомления', max_length=500)
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    link = models.CharField('Ссылка', max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'Уведомление чата'
        verbose_name_plural = 'Уведомления чатов'
        ordering = ['-created_at']

    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.content[:50]}"


class PinnedMessage(models.Model):
    """Закрепленные сообщения в чатах"""

    chat = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='pinned_messages',
        verbose_name='Чат'
    )
    message = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='pinned',
        verbose_name='Сообщение'
    )
    pinned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pinned_messages',
        verbose_name='Закрепил'
    )
    pinned_at = models.DateTimeField('Дата закрепления', auto_now_add=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Закрепленное сообщение'
        verbose_name_plural = 'Закрепленные сообщения'

    def __str__(self):
        return f"Закреплено в {self.chat.title}"


class Integration(models.Model):
    """Интеграции с внешними системами"""

    INTEGRATION_TYPES = [
        ('JIRA', 'Jira'),
        ('GITHUB', 'GitHub'),
        ('GITLAB', 'GitLab'),
    ]

    type = models.CharField('Тип', max_length=50, choices=INTEGRATION_TYPES)
    name = models.CharField('Название', max_length=100)
    webhook_url = models.URLField('Webhook URL', blank=True, null=True)
    api_key = models.CharField('API Key', max_length=255, blank=True, null=True)
    config = models.JSONField('Конфигурация', default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Интеграция'
        verbose_name_plural = 'Интеграции'

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"
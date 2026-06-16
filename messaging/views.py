from .markdown_utils import format_message
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Message
from .forms import SendMessageForm
from django.contrib import messages


@login_required
def inbox(request):
    return render(request, "messaging/inbox.html", {
        "inbox_items": Message.objects.filter(to_user=request.user)[:50],
        "outbox_items": Message.objects.filter(from_user=request.user)[:50],
        "form": SendMessageForm(),
    })

@login_required
def send_message(request):
    if request.method != "POST":
        return redirect("messaging:inbox")
    form = SendMessageForm(request.POST)
    if form.is_valid():
        to_user = User.objects.get(username=form.cleaned_data["to_username"])
        Message.objects.create(
            from_user=request.user,
            to_user=to_user,
            subject=form.cleaned_data["subject"],
            body=form.cleaned_data["body"],
        )
        return redirect("messaging:inbox")
    return render(request, "messaging/inbox.html", {
        "inbox_items": Message.objects.filter(to_user=request.user)[:50],
        "outbox_items": Message.objects.filter(from_user=request.user)[:50],
        "form": form,
    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatMembership, ChatMessage, MessageAttachment, ChatNotification


@login_required
def chat_list(request):
    """Список групповых чатов пользователя с автооткрытием первого"""
    memberships = ChatMembership.objects.filter(
        user=request.user,
        left_at__isnull=True
    ).select_related('chat').order_by('chat__title')  # ← сортировка по алфавиту

    chats = []
    for m in memberships:
        chat = m.chat
        last_msg = chat.messages.filter(is_deleted=False).first()
        unread = chat.messages.exclude(read_by=request.user).count() if last_msg else 0

        chats.append({
            'chat': chat,
            'last_msg': last_msg,
            'unread': unread,
            'role': m.role_in_chat,
        })

    # Проверяем, выбран ли конкретный чат (GET-параметр)
    selected_chat = None
    chat_messages = []

    chat_id = request.GET.get('chat')

    # Если чат не выбран — открываем первый из списка
    if not chat_id and chats:
        selected_chat = chats[0]['chat']
        chat_id = selected_chat.id
    elif chat_id:
        try:
            selected_chat = ChatRoom.objects.get(
                id=chat_id,
                members__user=request.user,
                members__left_at__isnull=True
            )
        except ChatRoom.DoesNotExist:
            # Если чат не найден — берём первый
            if chats:
                selected_chat = chats[0]['chat']

    # Загружаем сообщения для выбранного чата
    if selected_chat:
        chat_messages = selected_chat.messages.filter(
            is_deleted=False
        ).select_related('sender').prefetch_related('attachments', 'read_by').order_by('sent_at')[:50]

        # Отмечаем как прочитанные
        unread_msgs = selected_chat.messages.exclude(read_by=request.user)
        for msg in unread_msgs:
            msg.read_by.add(request.user)

        # Обновляем last_read_message
        try:
            membership = ChatMembership.objects.get(user=request.user, chat=selected_chat)
            last_message = selected_chat.messages.first()
            if last_message:
                membership.last_read_message = last_message
                membership.save(update_fields=['last_read_message'])
        except ChatMembership.DoesNotExist:
            pass

        for msg in chat_messages:
            msg.content = format_message(msg.content)

    return render(request, 'messaging/chat_list.html', {
        'chats': chats,
        'selected_chat': selected_chat,
        'chat_messages': chat_messages,
    })

@login_required
def chat_room(request, chat_id):
    """Комната группового чата"""
    chat = get_object_or_404(
        ChatRoom.objects.filter(members__user=request.user),
        id=chat_id
    )

    messages = chat.messages.filter(
        is_deleted=False
    ).select_related('sender').prefetch_related('attachments', 'read_by').order_by('-sent_at')[:50]

    # Отмечаем как прочитанные
    unread = chat.messages.exclude(read_by=request.user)
    for msg in unread:
        msg.read_by.add(request.user)

    # Обновляем last_read_message
    membership = ChatMembership.objects.get(user=request.user, chat=chat)
    last_message = chat.messages.first()
    if last_message:
        membership.last_read_message = last_message
        membership.save(update_fields=['last_read_message'])

    return render(request, 'messaging/chat_room.html', {
        'chat': chat,
        'messages': reversed(list(messages)),
    })


@login_required
def send_chat_message(request, chat_id):
    """Отправка сообщения в групповой чат (AJAX) с поддержкой файлов"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)

    chat = get_object_or_404(ChatRoom, id=chat_id)
    content = request.POST.get('content', '').strip()

    if not content and not request.FILES:
        return JsonResponse({'error': 'Пустое сообщение'}, status=400)

    message = ChatMessage.objects.create(
        chat=chat,
        sender=request.user,
        content=content
    )

    # Обработка загруженных файлов
    attachments_data = []
    for file in request.FILES.getlist('files'):
        import os
        from django.core.files.storage import default_storage

        # Сохраняем файл
        file_path = default_storage.save(
            f'chat_attachments/{chat_id}/{file.name}',
            file
        )

        attachment = MessageAttachment.objects.create(
            message=message,
            file_name=file.name,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file.size,
            file=file
        )

        attachments_data.append({
            'id': attachment.id,
            'file_name': attachment.file_name,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'is_image': attachment.is_image,
            'url': attachment.file.url if attachment.file else '#'
        })

    # Обновляем last_message у чата
    chat.last_message = message
    chat.save(update_fields=['last_message'])

    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'content_formatted': format_message(message.content),
            'sender': message.sender.get_full_name() or message.sender.username,
            'sent_at': message.sent_at.strftime('%H:%M'),
            'attachments': attachments_data,
        }
    })


@login_required
def get_chat_messages(request, chat_id):
    """Получение новых сообщений (AJAX)"""
    chat = get_object_or_404(ChatRoom, id=chat_id)
    after_id = request.GET.get('after', 0)

    messages_qs = chat.messages.filter(
        id__gt=after_id,
        is_deleted=False
    ).select_related('sender').order_by('sent_at')

    data = [{
        'id': msg.id,
        'content': msg.content,
        'content_formatted': format_message(msg.content),  # ← форматированная версия
        'sender': msg.sender.get_full_name() or msg.sender.username,
        'sent_at': msg.sent_at.strftime('%H:%M'),
        'is_own': msg.sender == request.user,
    } for msg in messages_qs]

    return JsonResponse({'messages': data})


@login_required
def create_chat_room(request):
    """Создание нового группового чата"""
    if request.method == 'POST':
        title = request.POST.get('title')
        chat_type = request.POST.get('type', 'GROUP')
        member_ids = request.POST.getlist('members')

        chat = ChatRoom.objects.create(
            title=title,
            type=chat_type,
            created_by=request.user
        )

        # Добавляем создателя как владельца
        ChatMembership.objects.create(
            user=request.user,
            chat=chat,
            role_in_chat='OWNER'
        )

        # Добавляем выбранных участников
        for user_id in member_ids:
            user = User.objects.get(id=user_id)
            ChatMembership.objects.get_or_create(
                user=user,
                chat=chat,
                defaults={'role_in_chat': 'MEMBER'}
            )

        messages.success(request, f'Чат "{title}" создан!')
        return redirect('messaging:chat_room', chat_id=chat.id)

    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    return render(request, 'messaging/create_chat.html', {
        'users': users
    })


@login_required
def chat_members(request, chat_id):
    """Участники чата"""
    chat = get_object_or_404(ChatRoom, id=chat_id)
    memberships = ChatMembership.objects.filter(
        chat=chat,
        left_at__isnull=True
    ).select_related('user')

    return render(request, 'messaging/chat_members.html', {
        'chat': chat,
        'memberships': memberships
    })


@login_required
def search_messages(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id, members__user=request.user)
    query = request.GET.get('q', '').strip()

    messages_list = []
    search_time = 0

    if query:
        start = time.time()
        messages_list = chat.messages.filter(
            content__icontains=query,
            is_deleted=False
        ).select_related('sender').order_by('-sent_at')[:50]
        search_time = round(time.time() - start, 3)

    return render(request, 'messaging/search_results.html', {
        'chat': chat,
        'query': query,
        'messages_list': messages_list,
        'search_time': search_time,
    })


@login_required
def pin_message(request, chat_id, message_id):
    """Закрепление/открепление сообщения"""
    chat = get_object_or_404(ChatRoom, id=chat_id)
    message = get_object_or_404(ChatMessage, id=message_id, chat=chat)


    pinned, created = PinnedMessage.objects.get_or_create(
        chat=chat,
        message=message,
        pinned_by=request.user,
        defaults={'is_active': True}
    )

    if not created:
        # Если уже закреплено — открепляем
        pinned.is_active = not pinned.is_active
        pinned.save()

    return JsonResponse({
        'success': True,
        'is_pinned': pinned.is_active,
        'message_id': message.id
    })


import json
import hashlib
import hmac
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Integration, ChatRoom, ChatMessage, ChatMembership


@csrf_exempt
def webhook_receiver(request, integration_id):
    """
    Приём webhook-уведомлений от внешних систем (Jira, GitHub, GitLab).

    Пример запроса от GitHub:
    POST /messages/webhook/1/
    Headers: X-Hub-Signature-256: sha256=...
    Body: {"commits": [...], "repository": {...}}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)

    # Получаем интеграцию
    integration = get_object_or_404(Integration, id=integration_id, is_active=True)

    # Проверяем секретный ключ (если задан)
    api_key = integration.api_key
    if api_key:
        # Для GitHub: X-Hub-Signature-256
        signature = request.headers.get('X-Hub-Signature-256', '')
        if signature:
            expected = 'sha256=' + hmac.new(
                api_key.encode(),
                request.body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return JsonResponse({'error': 'Неверная подпись'}, status=403)

    # Разбираем тело запроса
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный JSON'}, status=400)

    # Формируем сообщение в зависимости от типа интеграции
    chat = None
    if integration.config and 'chat_id' in integration.config:
        chat = ChatRoom.objects.filter(id=integration.config['chat_id']).first()

    if integration.type == 'GITHUB':
        message_text = format_github_webhook(data)
    elif integration.type == 'GITLAB':
        message_text = format_gitlab_webhook(data)
    elif integration.type == 'JIRA':
        message_text = format_jira_webhook(data)
    else:
        message_text = f"Webhook от {integration.name}: {json.dumps(data, indent=2)}"

    # Если указан чат для уведомлений — отправляем сообщение
    if chat and message_text:
        try:
            bot_user = User.objects.get(username='admin')  # Или создайте бота
        except User.DoesNotExist:
            bot_user = User.objects.first()

        ChatMessage.objects.create(
            chat=chat,
            sender=bot_user,
            content=message_text
        )

    return JsonResponse({
        'success': True,
        'type': integration.type,
        'message': message_text[:200] if message_text else 'Обработано'
    })


def format_github_webhook(data):
    """Форматирует уведомление от GitHub"""
    if 'commits' in data and data['commits']:
        repo = data.get('repository', {}).get('full_name', 'неизвестный репозиторий')
        commits = data['commits']
        lines = [f"📦 **Новые коммиты в {repo}:**"]
        for commit in commits[:5]:
            author = commit.get('author', {}).get('name', 'неизвестный')
            message = commit.get('message', '').split('\n')[0]
            lines.append(f"  • {author}: {message}")
        if len(commits) > 5:
            lines.append(f"  • ... и ещё {len(commits) - 5} коммитов")
        return '\n'.join(lines)

    if 'pull_request' in data:
        pr = data['pull_request']
        return f"🔀 **Pull Request:** {pr['title']} ({pr['html_url']})"

    return None


def format_gitlab_webhook(data):
    """Форматирует уведомление от GitLab"""
    object_kind = data.get('object_kind', '')

    if object_kind == 'push':
        commits = data.get('commits', [])
        repo = data.get('project', {}).get('name', 'неизвестный проект')
        lines = [f"📦 **Новые коммиты в {repo}:**"]
        for commit in commits[:5]:
            author = commit.get('author', {}).get('name', 'неизвестный')
            message = commit.get('message', '').split('\n')[0]
            lines.append(f"  • {author}: {message}")
        return '\n'.join(lines)

    if object_kind == 'merge_request':
        mr = data.get('object_attributes', {})
        return f"🔀 **Merge Request:** {mr.get('title')} ({mr.get('url')})"

    return None


def format_jira_webhook(data):
    """Форматирует уведомление от Jira"""
    issue = data.get('issue', {})
    if issue:
        key = issue.get('key', '')
        fields = issue.get('fields', {})
        summary = fields.get('summary', '')
        status = fields.get('status', {}).get('name', '')
        return f"🎫 **Jira {key}:** {summary} (статус: {status})"
    return None
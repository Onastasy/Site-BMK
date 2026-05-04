from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Message
from .forms import SendMessageForm

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
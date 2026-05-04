import re
import markdown
from django.contrib.auth.models import User
from django.urls import reverse


def parse_markdown(text):
    """
    Преобразует Markdown-подобный синтаксис в HTML.
    Поддерживает: **жирный**, *курсив*, `код`, ```блок кода```, списки
    """
    if not text:
        return ''

    # Заменяем Markdown-синтаксис на HTML
    # **жирный**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # *курсив*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # `код` (инлайн)
    text = re.sub(r'`([^`]+)`', r'<code style="background:#f4f4f4;padding:2px 6px;border-radius:3px;">\1</code>', text)

    # ```блок кода```
    text = re.sub(
        r'```(\w*)\n?(.+?)```',
        r'<pre style="background:#2d2d2d;color:#f8f8f2;padding:10px;border-radius:5px;overflow-x:auto;"><code>\2</code></pre>',
        text,
        flags=re.DOTALL
    )

    # - элемент списка
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)

    # > цитата
    text = re.sub(
        r'^> (.+)$',
        r'<blockquote style="border-left:3px solid #007bff;padding-left:10px;margin:5px 0;color:#666;">\1</blockquote>',
        text,
        flags=re.MULTILINE
    )

    # Переносы строк в <br>
    text = text.replace('\n\n', '</p><p>')
    text = text.replace('\n', '<br>')
    text = f'<p>{text}</p>'

    return text


def parse_mentions(text):
    """
    Находит упоминания вида @username и заменяет на ссылки на профиль
    """
    if not text:
        return text

    def replace_mention(match):
        username = match.group(1)
        try:
            user = User.objects.get(username=username)
            return f'<a href="/accounts/profile/" class="mention" style="color:#007bff;font-weight:bold;">@{user.get_full_name() or username}</a>'
        except User.DoesNotExist:
            return f'@{username}'

    text = re.sub(r'@(\w+)', replace_mention, text)
    return text


def format_message(text):
    """Полное форматирование сообщения: Markdown + упоминания"""
    text = parse_markdown(text)
    text = parse_mentions(text)
    return text
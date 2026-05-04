import re
from django.contrib.auth.models import User


def format_message(text):
    """
    Преобразует Markdown-подобный синтаксис в HTML.
    Поддерживает: **жирный**, *курсив*, `код`, @упоминания
    """
    if not text:
        return ''

    # Экранируем HTML, чтобы избежать XSS
    text = escape_html(text)

    # **жирный**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # *курсив*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # `код` (инлайн)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # @упоминания
    def replace_mention(match):
        username = match.group(1)
        try:
            user = User.objects.get(username=username)
            name = user.get_full_name() or username
            return f'<span class="mention">@{name}</span>'
        except User.DoesNotExist:
            return f'@{username}'

    text = re.sub(r'@(\w+)', replace_mention, text)

    # Переносы строк
    text = text.replace('\n', '<br>')

    return text


def escape_html(text):
    """Экранирует HTML-символы"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
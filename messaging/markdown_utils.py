import re
from django.contrib.auth.models import User


def format_message(text):
    """
    Простое форматирование: **жирный**, *курсив*, `код`, @упоминания.
    Возвращает готовый HTML.
    """
    if not text:
        return ''

    # **жирный**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # *курсив*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # `инлайн-код`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # @упоминания
    def replace_mention(match):
        username = match.group(1)
        try:
            user = User.objects.get(username=username)
            name = user.get_full_name() or username
            return f'<span style="color:#007bff;font-weight:bold;">@{name}</span>'
        except User.DoesNotExist:
            return f'@{username}'

    text = re.sub(r'@(\w+)', replace_mention, text)

    # Переносы строк
    text = text.replace('\n', '<br>')

    return text
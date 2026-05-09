import re
from django.contrib.auth.models import User


def format_message(text):
    """
    Преобразует Markdown-подобный синтаксис в HTML.
    Поддерживает: **жирный**, *курсив*, `код`, ```блок кода```, @упоминания
    """
    if not text:
        return ''

    # Экранируем HTML
    text = escape_html(text)

    # Сохраняем блоки кода ДО замены переносов
    code_blocks = []

    def extract_code(match):
        lang = match.group(1) or ''
        code = match.group(2)
        # Сохраняем оригинальные переносы
        code_blocks.append((lang, code))
        placeholder = f'%%CODEBLOCK{len(code_blocks) - 1}%%'
        return placeholder

    # Находим все блоки кода и заменяем на плейсхолдеры
    text = re.sub(r'```(\w*)\s*\n(.+?)```', extract_code, text, flags=re.DOTALL)

    # **жирный**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # *курсив*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # `инлайн-код` (только после удаления блоков)
    text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)

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

    # Переносы строк для обычного текста
    text = text.replace('\n', '<br>')

    # Восстанавливаем блоки кода с правильным HTML
    for i, (lang, code) in enumerate(code_blocks):
        lang_class = f' class="language-{lang}"' if lang else ''
        # ВАЖНО: не заменяем \n на <br> внутри кода
        formatted = f'<pre><code{lang_class}>{code}</code></pre>'
        text = text.replace(f'%%CODEBLOCK{i}%%', formatted)

    return text


def escape_html(text):
    """Экранирует HTML-символы"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
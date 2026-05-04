def get_breadcrumbs(request):
    """Формирует хлебные крошки на основе URL"""
    path = request.path.strip('/').split('/')
    breadcrumbs = [{'name': 'Главная', 'url': '/'}]

    url_names = {
        'about': 'О сайте',
        'about-us': 'О нас',
        'advantages': 'Преимущества',
        'team': 'Наша команда',
        'vacancies': 'Вакансии',
        'contact': 'Контакты',
        'sitemap': 'Карта сайта',
        'search': 'Поиск',
        'privacy': 'Политика конфиденциальности',
        'news': 'Новости',
        'messages': 'Сообщения',
        'inbox': 'Входящие',
        'accounts': 'Аккаунт',
        'login': 'Вход',
        'register': 'Регистрация',
        'profile': 'Профиль',
        'dashboard': 'Личный кабинет',
        'employees': 'Сотрудники',
        'admin-panel': 'Админ-панель',
        'users': 'Пользователи',
        'groups': 'Группы',
        'settings': 'Настройки',
        'chats': 'БМК Чат',
        'chat_room': 'Чат',
        'chat_members': 'Участники',
    }

    url = ''
    for part in path:
        if part and not part.isdigit():
            url += f'/{part}'
            name = url_names.get(part, part.replace('-', ' ').title())
            breadcrumbs.append({'name': name, 'url': url})

    return breadcrumbs


## Запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py bootstrap_demo
python manage.py runserver
```
Открой: http://127.0.0.1:8000

## Демо-учётки
- admin / admin123 (группа admin, is_staff=True → доступ к /admin/)
- user / user123 (группа user)

## Сценарии создания пользователя
### Самостоятельно пользователем
1) /accounts/register/ → создать логин/пароль  
2) /accounts/login/ → войти  
3) /messages/ → отправлять сообщения

### Сотрудником (admin)
Через /admin/:
1) admin/admin123 → войти в Django Admin  
2) создать User и назначить группу admin/user, при необходимости is_staff  
3) пользователь входит через /accounts/login/


## Дополнительные страницы (контент)
- /about-us/ — О нас
- /advantages/ — Преимущества
- /team/ — Наша команда
- /vacancies/ — Вакансии

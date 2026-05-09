# Инструкция по миграции с SQLite на PostgreSQL

## Локальная разработка (SQLite)
Ничего не требуется, проект работает из коробки.

## Продакшен (PostgreSQL)

### 1. Установка PostgreSQL
sudo apt install postgresql postgresql-contrib

### 2. Создание базы данных
sudo -u postgres psql
CREATE USER bmk_user WITH PASSWORD 'ваш_пароль';
CREATE DATABASE bmk_chat OWNER bmk_user;
\q

### 3. Переменные окружения
DB_ENGINE=postgresql
DB_NAME=bmk_chat
DB_USER=bmk_user
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432

### 4. Применение миграций
python manage.py migrate

### 5. Загрузка тестовых данных
python manage.py shell < scripts/load_test_data.py
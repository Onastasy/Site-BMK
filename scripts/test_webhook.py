"""
Тестовый скрипт для отправки webhook локально.
Запуск: python scripts/test_webhook.py
"""
import requests
import json

# URL webhook (предполагаем, что интеграция с id=1 настроена)
url = "http://127.0.0.1:8000/messages/webhook/1/"

# Тестовые данные (GitHub push)
test_data = {
    "commits": [
        {"author": {"name": "developer"}, "message": "fix: исправлена ошибка в чате"},
        {"author": {"name": "developer"}, "message": "feat: добавлена подсветка кода"}
    ],
    "repository": {"full_name": "Onastasy/Site-BMK"}
}

response = requests.post(url, json=test_data)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.json()}")
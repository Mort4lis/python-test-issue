# Python test issue

Репозиторий: https://github.com/Mort4lis/python-test-issue.git

# Зависимости

- [Docker](https://docs.docker.com/engine/install/)  
- [Docker-compose](https://docs.docker.com/compose/install/)

# Установка

```bash
# Клонируем репозиторий
git clone https://github.com/Mort4lis/python-test-issue.git
cd python-test-issue

# Запуск приложения
docker-compose up --build

# Инициализация БД (создание таблиц, заполнение тестовыми данными)
docker-compose run --rm web python init_db.py
```

Проверка кода (pep8, pep257)
```bash
docker-compose run --rm web flake8
```

# Использование

```bash
# Аутентификация
curl -X POST http://127.0.0.1:8080/login -d '{"login": "user1", "password": "user1"}'
{"token": "<access-token>"}

# Получить, например, список всех продуктов
curl http://127.0.0.1:8080/products -H "Authorization: Bearer <access-token>"
```
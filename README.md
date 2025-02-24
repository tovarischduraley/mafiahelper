# Mafia Helper Bot
Телеграм бот помощник для спортивной мафии

### Основные функции бота
- Протоколирование игр
- Ведение статистики игроков

### Основные функции бота

Для работы бота требуется `.env` файл в корне проекта со следующими переменными окружения

```
TELEGRAM_BOT_TOKEN
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
ADMIN_ID                # Telegram ID пользователя  
```

Запуск осуществляется через `docker compose`

```
docker compose up --build
```

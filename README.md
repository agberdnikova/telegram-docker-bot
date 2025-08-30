# Telegram Bot with Docker

Простой Telegram-бот на Python:
- отвечает текстом через OpenAI,
- умеет рисовать картинки по команде `/image`.

## 🚀 Запуск
1. Склонировать репозиторий:
   ```bash
   git clone https://github.com/agberdnikova/telegram-docker-bot.git
   cd telegram-docker-bot
Создать файл .env с ключами:

env
Копировать код
TELEGRAM_BOT_TOKEN=ваш_телеграм_токен
OPENAI_API_KEY=ваш_openai_api_key
Запустить:

bash
Копировать код
docker compose up -d --build
Теперь бот работает 🎉

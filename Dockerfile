# Базовый образ с Python
FROM python:3.11-slim

# Чтоб логи сразу печатались и кэш pip не рос
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Рабочая папка в контейнере
WORKDIR /app

# Сначала зависимости (используем кэш сборки)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом сам код бота
COPY main.py .

# Команда запуска
CMD ["python", "main.py"]

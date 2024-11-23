# Базовый образ Python
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev gcc libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов requirements
COPY requirements.txt .

# Установка зависимостей проекта
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Установка переменной окружения для Django
ENV DJANGO_SETTINGS_MODULE=ServForAndroidApp.settings

# Открытие порта 8000
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "ServForAndroidApp/manage.py", "runserver", "0.0.0.0:8000"]

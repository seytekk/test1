# 1. Базовый образ (например, Python 3.11 slim)
FROM python:3.11-slim

# 2. Рабочая директория в контейнере
WORKDIR /bloglite

# 3. Копируем файл зависимостей
COPY requirements.txt .

# 4. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем всё остальное
COPY . .

# 6. Открываем порт (если нужно)
EXPOSE 8000

# 7. Команда запуска
CMD ["python", "bloglite/manage.py", "runserver", "0.0.0.0:8000"]

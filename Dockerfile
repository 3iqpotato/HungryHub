# Използваме официалния Python образ
FROM python:3.13-rc-slim

# Създаваме работна директория
WORKDIR /app

# Копираме requirements.txt и инсталираме зависимостите
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копираме останалите файлове
COPY . .

# Команда за стартиране на приложението
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
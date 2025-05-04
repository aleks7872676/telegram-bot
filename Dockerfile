FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей для psycopg2
RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание таблиц при старте
RUN python -c "from bot import Base, engine; Base.metadata.create_all(engine)"

CMD ["python", "bot.py"]

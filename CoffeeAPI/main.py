import os
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, Column, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

# Строка подключения к базе данных
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://myuser:mypassword@localhost:5432/coffee_db')

# Создание движка и сессии для работы с базой данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель для хранения транзакций
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    payment_amount = Column(Numeric(10, 2), nullable=False)
    coffee_type = Column(String, nullable=False)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI
app = FastAPI()

# Инициализация инструментатора для Prometheus
instrumentator = Instrumentator()

# Кастомные метрики
coffee_request_counter = Counter(
    'coffee_requests_total', 
    'Total number of requests to buy coffee', 
    ['coffee_type']
)

request_latency = Histogram(
    'request_latency_seconds', 
    'Latency of HTTP requests in seconds'
)

# Модель для запроса оплаты
class Payment(BaseModel):
    payment_amount: Decimal

# Логика для определения типа кофе
def get_coffee_type(payment_amount: Decimal) -> str:
    if payment_amount < Decimal('2.00'):
        return "Espresso"
    elif Decimal('2.00') <= payment_amount < Decimal('3.00'):
        return "Latte"
    else:
        return "Cappuccino"

# Эндпоинт для покупки кофе
@app.post("/buy_coffee/")
def buy_coffee(payment: Payment):
    coffee_type = get_coffee_type(payment.payment_amount)
    
    # Инкрементируем кастомный счетчик
    coffee_request_counter.labels(coffee_type=coffee_type).inc()

    # Создание записи о транзакции
    transaction = Transaction(
        id=str(uuid4()),
        payment_amount=payment.payment_amount,
        coffee_type=coffee_type
    )

    # Сохранение записи в базу данных
    db = SessionLocal()
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.close()

    return {
        "transaction_id": transaction.id,
        "timestamp": transaction.timestamp,
        "payment_amount": str(transaction.payment_amount),
        "coffee_type": transaction.coffee_type
    }

# Запуск инструментатора при старте приложения
@app.on_event("startup")
def setup_prometheus():
    instrumentator.instrument(app).expose(app)
    
    # Если нужно добавить кастомные метрики вручную
    instrumentator.add(
        lambda: coffee_request_counter
    )
    instrumentator.add(
        lambda: request_latency
    )

    # Обновление метрик
    # Вы можете также обновить метрики по мере необходимости

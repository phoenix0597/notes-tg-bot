from sqlalchemy import Column, Integer, String, BigInteger
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)  # Новый столбец для Telegram ID
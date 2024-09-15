from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

# Таблица-связка (association table) для связи "многие ко многим"
note_tags = Table(
    'note_tags', Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    # tags = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    # Связь "многие ко многим" с тегами
    tags = relationship("Tag", secondary=note_tags, back_populates="notes", lazy='selectin')


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Обратная связь с заметками
    notes = relationship("Note", secondary=note_tags, back_populates="tags")
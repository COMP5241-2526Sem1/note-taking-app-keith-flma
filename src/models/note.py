from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from src.models.user import db

class Note(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(200), nullable=False)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(db.String(500), nullable=True)
    event_date: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)
    event_time: Mapped[Optional[str]] = mapped_column(db.String(20), nullable=True)
    order_index: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'event_date': self.event_date,
            'event_time': self.event_time,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


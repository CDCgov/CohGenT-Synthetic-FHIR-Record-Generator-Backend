from typing import Any

from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from api.database.database_client import Base

class SampleSettings(Base):
    __tablename__ = 'samples'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<JsonRecord(id={self.id}, name='{self.name}', data={self.data})>"
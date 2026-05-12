from sqlalchemy import Column, Integer, String, JSON
from api.database.database_client import Base

class SampleSettings(Base):
    __tablename__ = 'samples'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    data = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<JsonRecord(id={self.id}, name='{self.name}', data={self.data})>"
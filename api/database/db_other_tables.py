from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from api.database.database_client import Base

'''
Contains Tables not tied to a specific Feature
'''
class TribalAffiliation(Base):
    __tablename__ = 'tribal_affiliation'
    
    affiliation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    display: Mapped[str] = mapped_column(String(500))
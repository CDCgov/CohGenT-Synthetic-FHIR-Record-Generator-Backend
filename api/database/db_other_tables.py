from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from api.database.database_client import Base

'''
Contains Tables not tied to a specific Feature
'''
class TribalAffiliation(Base):
    __tablename__ = 'tribal_affiliation'
    
    affiliation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    system: Mapped[str] = mapped_column(String(255), nullable=False, default="http://terminology.hl7.org/CodeSystem/v3-TribalEntityUS", server_default="http://terminology.hl7.org/CodeSystem/v3-TribalEntityUS")
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    display: Mapped[str] = mapped_column(String(500))

    def __repr__(self):
        return f"<TribalAffiliation(id={self.affiliation_id}, system={self.system}, code='{self.code}', display='{self.display}')>"

class ProviderEntity(Base):
    __tablename__ = 'provider_entity'
    
    # Primary key - matches entityId from JSON files
    entity_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    
    # Basic info for lookups
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Store full JSON entity definition
    entity_json: Mapped[str] = mapped_column(String, nullable=False)
    
    def __repr__(self):
        return f"<ProviderEntity(id={self.entity_id}, type={self.resource_type}, name='{self.display_name}')>"
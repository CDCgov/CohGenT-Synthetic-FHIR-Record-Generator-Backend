from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
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


class Industry(Base):
    """North American Industry Classification System (NAICS) codes"""
    __tablename__ = 'industry'
    
    industry_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    system: Mapped[str] = mapped_column(String(255), nullable=False, default="urn:oid:2.16.840.1.114222.4.5.336", server_default="urn:oid:2.16.840.1.114222.4.5.336")
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    display: Mapped[str] = mapped_column(String(500))

    occupations: Mapped[list["Occupation"]] = relationship("Occupation", back_populates="industry")

    def __repr__(self):
        return f"<Industry(code='{self.code}', display='{self.display}')>"

class Occupation(Base):
    """Standard Occupational Classification (SOC) codes"""
    __tablename__ = 'occupation'
    
    occupation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    system: Mapped[str] = mapped_column(String(255), nullable=False, default="urn:oid:2.16.840.1.114222.4.5.339", server_default="urn:oid:2.16.840.1.114222.4.5.339")
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    display: Mapped[str] = mapped_column(String(500))
    industry_id: Mapped[int] = mapped_column(Integer, ForeignKey('industry.industry_id'), nullable=False)

    industry: Mapped["Industry"] = relationship("Industry", back_populates="occupations")

    def __repr__(self):
        return f"<Occupation(id={self.occupation_id}, system={self.system}, code='{self.code}', display='{self.display}')>"


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
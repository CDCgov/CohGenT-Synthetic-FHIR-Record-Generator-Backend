from sqlalchemy import Column, Index, Integer, String, Float, Enum as SQLEnum
from api.database.database_client import Base
from enum import Enum as PyEnum

class ValueTypeEnum(str, PyEnum):
    QUANTITY = "Quantity"
    STRING = "string"

class ValuePreset(Base):
    __tablename__ = "valuepreset"
    
    # concept_id = Column(Integer, primary_key=True, index=True)
    code = Column(String, primary_key=True, index=True)
    system = Column(String, primary_key=True, index=True)
    preset_name = Column(String, primary_key=True, nullable=False, index=True)
    value_type = Column(
            SQLEnum(ValueTypeEnum),
            nullable=False
        )
    quantity_min = Column(Float, nullable=True)
    quantity_max = Column(Float, nullable=True)
    quantity_unit = Column(String, nullable=True)
    priority = Column(Integer, default=4)

    __table_args__ = (
        # Composite indexes
        Index('ix_valuepreset_preset_code', 'preset_name', 'code'),
        Index('ix_valuepreset_preset_system', 'preset_name', 'system'),
        Index('ix_valuepreset_name_system_code', 'preset_name', 'system', 'code'),
    )
    
    def __repr__(self):
        return f"<Concept(id={self.code}, system={self.system}, name='{self.preset_name}', type='{self.value_type}', priority='{self.priority}')>"
    

    
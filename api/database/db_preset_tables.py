from sqlalchemy import Index, Integer, String, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from api.database.database_client import Base
from enum import Enum as PyEnum

class ValueTypeEnum(str, PyEnum):
    QUANTITY = "Quantity"
    STRING = "string"

class ValuePreset(Base):
    __tablename__ = "valuepreset"
    
    # concept_id = Column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    system: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    preset_name: Mapped[str] = mapped_column(String, primary_key=True, nullable=False, index=True)
    value_type: Mapped[ValueTypeEnum] = mapped_column(
            SQLEnum(ValueTypeEnum),
            nullable=False
        )
    quantity_min: Mapped[int | None] = mapped_column(Float, nullable=True)
    quantity_max: Mapped[int | None] = mapped_column(Float, nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[str] = mapped_column(Integer, default=4)

    __table_args__ = (
        # Composite indexes
        Index('ix_valuepreset_preset_code', 'preset_name', 'code'),
        Index('ix_valuepreset_preset_system', 'preset_name', 'system'),
        Index('ix_valuepreset_name_system_code', 'preset_name', 'system', 'code'),
    )
    
    def __repr__(self):
        return f"<Concept(id={self.code}, system={self.system}, name='{self.preset_name}', type='{self.value_type}', priority='{self.priority}')>"
    

    
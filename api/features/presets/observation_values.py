from sqlalchemy.orm import Session
from api.database.db_preset_tables import ValuePreset
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from api.models.requests.value_preset_requests import CreateValuePreset, DeleteValuePreset
from fastapi import HTTPException, status

def create_value_preset(post_body: CreateValuePreset, db: Session):
    # Check if it already exists...
    existing = db.query(ValuePreset).filter(
        ValuePreset.code == post_body.code,
        ValuePreset.system == post_body.system,
        ValuePreset.preset_name == post_body.preset_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Conflict",
                "message": f"Value preset with that name for that code and system already exists",
                "code": post_body.code,
                "system": post_body.system,
                "presetName": post_body.preset_name
            }
        )
    try:
        preset_value = ValuePreset(**post_body.model_dump(exclude_none=True))
        print(post_body)
        print(preset_value)
        db.add(preset_value)
        db.commit()
        db.refresh(preset_value)
        
        # Verify creation
        created_preset = db.query(ValuePreset).filter(
            ValuePreset.code == preset_value.code,
            ValuePreset.system == preset_value.system,
            ValuePreset.preset_name == preset_value.preset_name
        ).first()
        
        if not created_preset:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify creation of value preset in database. Status not known."
            )
        
        return created_preset

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
    )

def delete_value_preset(post_body: DeleteValuePreset, db: Session) -> bool:
    value_preset_to_delete = db.query(ValuePreset).filter(
        ValuePreset.code == post_body.code,
        ValuePreset.system == post_body.system,
        ValuePreset.preset_name == post_body.preset_name
    ).first()
    
    if not value_preset_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Value preset not found"
        )
    
    db.delete(value_preset_to_delete)
    db.commit()
    
    confirm_deletion = db.query(ValuePreset).filter(
        ValuePreset.code == post_body.code,
        ValuePreset.system == post_body.system,
        ValuePreset.preset_name == post_body.preset_name
    ).first()

    if not confirm_deletion:
        return value_preset_to_delete
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, deletion likely failed."
        )


def read_value_presets(code: str, system: str, db: Session):
    priority_order = case(
        (ValuePreset.preset_name.startswith("Low"), 1),
        (ValuePreset.preset_name.startswith("Normal"), 2),
        (ValuePreset.preset_name.startswith("High"), 3),
        else_=4
    )

    value_presets = db.query(ValuePreset).filter(
        ValuePreset.code == code,
        ValuePreset.system == system
    ).order_by(ValuePreset.priority, ValuePreset.preset_name).all()

    return value_presets
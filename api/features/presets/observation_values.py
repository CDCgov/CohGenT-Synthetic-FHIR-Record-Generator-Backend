from sqlalchemy.orm import Session
from api.database.db_preset_tables import ValuePreset
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from api.models.requests.value_preset_requests import CreateValuePreset, DeleteValuePreset
from fastapi import HTTPException, status
from typing import Set, Tuple

'''
Preset Cache
The Cache is used to quickly identify available presets when using Terminology Search.
'''
_preset_cache: Set[Tuple[str, str]] | None = None

def _load_preset_cache(db: Session) -> Set[Tuple[str,str]]:
    """Load all unique combinations of code/system into a set."""
    presets = db.query(
        ValuePreset.code,
        ValuePreset.system
    ).distinct().all()
    return {(preset.code, preset.system) for preset in presets}

def get_preset_cache(db: Session, force_refresh: bool = False) -> Set[Tuple[str, str]]:
    """Get the cached set of (code, system) tuples that have presets.
    
    Args:
        db: Database session
        force_refresh: If True, reload cache from database
    
    Returns:
        Set of (code, system) tuples that have value presets
    """
    global _preset_cache
    if _preset_cache is None or force_refresh:
        _preset_cache = _load_preset_cache(db)
    return _preset_cache

def invalidate_preset_cache():
    """Invalidate the preset cache, forcing reload on next access."""
    global _preset_cache
    _preset_cache = None

def has_value_presets(code: str, system: str, db: Session) -> bool:
    """Check if value presets exist for a given code and system combination.
    
    Uses cached data for O(1) lookup performance.
    
    Args:
        code: The concept code
        system: The FHIR system URI
        db: Database session
    
    Returns:
        True if presets exist, False otherwise
    """
    cache = get_preset_cache(db)
    return (code, system) in cache

'''
Value Preset CRUDS Operations
'''
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

        db.add(preset_value)
        db.commit()
        db.refresh(preset_value)

        # Invalidate current cache since a new preset was added.
        invalidate_preset_cache()
        
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

    # Invalidate current cache after preset deletion
    invalidate_preset_cache()
    
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
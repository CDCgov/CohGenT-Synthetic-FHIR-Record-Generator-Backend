from loguru import logger
from fastapi import Depends, Query, status, APIRouter
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.database_client import get_main_db
from api.models.requests.value_preset_requests import CreateValuePreset, DeleteValuePreset
from sqlalchemy.orm import Session
from api.models.responses.value_preset_respones import ValuePresetSearchResponse, ValuePresetResponse, SearchParameters, DeleteValuePresetResponse
from api.features.presets.condition_list import get_condition_list
from api.features.presets.observation_values import read_value_presets, create_value_preset, delete_value_preset


router = APIRouter()

"""
Returns list of demo conditions.
"""
@router.get("/presets/condition", response_class=PrettyJSONResponse)
async def get_preset_conditions():
    conditions = get_condition_list()
    return conditions

"""
Returns list of presets for a given Observation code.
"""
@router.get("/presets/observation/value", response_class=PrettyJSONResponse)
async def read_preset_observation_value(
    code: str = Query(..., description="Code (required)"),
    system: str = Query(..., description="System (required)"),
    db: Session = Depends(get_main_db)):
    
    table_results = read_value_presets(code, system, db)
    validted_results: list[ValuePresetResponse] = [ValuePresetResponse.model_validate(preset.__dict__) for preset in table_results]

    return ValuePresetSearchResponse(
        parameters= SearchParameters(code=code, system=system),
        count=len(table_results),
        results=validted_results
    )

"""
Create a new Observation value preset.
"""
@router.post("/presets/observation/value/create", status_code=status.HTTP_201_CREATED, response_class=PrettyJSONResponse)
async def create_preset_observation_value(post_body: CreateValuePreset, db: Session = Depends(get_main_db)):
    preset_value = create_value_preset(post_body, db)
    return preset_value

'''
Delete an Observation value preset.
'''
@router.delete("/presets/observation/value/delete", status_code=status.HTTP_200_OK, response_class=PrettyJSONResponse)
async def delete_preset_observation_value(post_body: DeleteValuePreset, db: Session = Depends(get_main_db)):
    delete_value_preset(post_body, db)
    return DeleteValuePresetResponse.model_validate({
        "message": "Successfully deleted value preset.",
        "status": status.HTTP_200_OK
    })

# TODO: Add update endpoint.
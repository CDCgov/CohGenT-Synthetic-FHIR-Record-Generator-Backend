
import os
import json
from api.models.use_case import UseCase
from api.models.entity import Entity
from fastapi import HTTPException
from pydantic import ValidationError
import pyjson5
from loguru import logger

path_to_common_entities= "./api/assets/commonentities/"
path_to_usecase_assets = "./api/assets/usecasetemplates/"

def read_use_case_assets() -> list[UseCase]:
    usecases: list[UseCase] = []
    for filename in os.listdir(path_to_usecase_assets):
        if filename.endswith(('.json', '.json5')): 
            filepath = os.path.join(path_to_usecase_assets, filename)
            try:
                with open(filepath, 'r') as f:
                    json_data = pyjson5.load(f)
                    use_case: UseCase = UseCase.model_validate(json_data)
                    usecases.append(use_case)
            except pyjson5.Json5Exception as e:
                #TODO: Swap to logging module.
                logger.error(f"Error decoding {filename},  Raising HTTP Exception for client. Error log: {e}")
                raise HTTPException(status_code=500, detail=f"JSON/JSON5 Decode Error. Please alert administrators. Error decoding {filename}: {e}.")

    return usecases

def get_use_case_by_id(use_case_id: str) -> UseCase:
    use_cases = read_use_case_assets()
    use_case = next((i for i in use_cases if i.use_case_id == use_case_id), None)
    try:
        use_case = UseCase.model_validate(use_case)
    except ValidationError:
        raise HTTPException(status_code=500, detail=f"Unable to locate usecase with id: {use_case_id}")
    return use_case


def read_common_entity(entity_id: str) -> Entity | None:
    entity: Entity | None = None
    filename = "".join("_" + c.lower() if c.isupper() else c for c in entity_id)
    filename = f"{filename}.json"
    if filename[0] == "_":
        filename = filename[1:]
    filepath = os.path.join(path_to_common_entities, filename)
    try:
        with open(filepath, 'r') as f:
            json_data = pyjson5.load(f)
            entity = Entity.model_validate(json_data)
    except pyjson5.Json5Exception as e:
        #TODO: Swap to logging module.
        logger.error(f"Error decoding {filename},  Raising HTTP Exception for client. Error log: {e}")
        raise HTTPException(status_code=500, detail=f"JSON/JSON5 Decode Error. Please alert administrators. Error decoding {filename}: {e}.")
    return entity
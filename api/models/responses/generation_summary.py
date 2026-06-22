from api.models.FHIR.bundle import Bundle
from typing import Optional
from datetime import datetime
from api.models.no_null_camel_model import NoNullCamelModel

class PatientRecordSummary(NoNullCamelModel):
    name: str
    birth_date: str
    sex: str
    resource_counts: dict[str, int]

class PatientContainer(NoNullCamelModel):
    summary: PatientRecordSummary
    fhir: Optional[Bundle] = None

class GenerationParameters(NoNullCamelModel):
    use_case_id: str
    seed: int
    count: int

class GenerationSummaryJson(NoNullCamelModel):
    time_stamp: str # ISO Formatted DateTime String with TimeZone
    generation_parameters: GenerationParameters 
    generation_summary: list[PatientContainer]

class GenerationSummaryBinary(NoNullCamelModel):
    time_stamp: str # ISO Formatted DateTime String with TimeZone
    generation_parameters: GenerationParameters 
    generation_summary: list[PatientContainer]
    data: str
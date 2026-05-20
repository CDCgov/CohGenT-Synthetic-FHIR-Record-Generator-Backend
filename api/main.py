'''
Initilization file.

Set title and version below. Additional tags may be set by enviroment.
'''
__title__ = "CohGenT - Cohort Generation Tool API"
__version__ = "1.0.2"

import io
import csv
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from loguru import logger
from api.features.presets.observation_values import get_preset_cache
from api.models.FHIR.bundle import Bundle
from api.models.FHIR.fhirresource import FHIRResource
from api.models.responses.generation_summary import PatientContainer
from api.utilities.logger_setup import setup_logging
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from api.utilities.file_reader import read_use_case_assets
from api.utilities.output_formatter import package_contents_as_json, package_contents_as_binary, package_contents_as_ndjson
from api.features.generation.generation import start_generation
from api.models.cohort_settings import CohortSettings
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.utilities.settings import get_settings
from api.models.responses.basic_response_models import InfoResponse, UseCaseCollectionResponse
from api.database.database_client import DatabaseClient
from api.database import db_preset_tables, db_sample_tables  # type: ignore - IMPORT IS REQUIRED TO BUILD TABLES
from api.routers import presets_router, terminology_router, samples_router
from api.models.cohort_settings import OutputFormat

from fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration # type: ignore
from fhir_sheets.core.conversion import create_transaction_bundle, create_resources # type: ignore

settings = get_settings()
app_title = f"{__title__} {settings.app_tag}".strip() if settings.app_tag else __title__
app_version = f"{__version__}-{settings.version_tag}".strip("-") if settings.version_tag else __version__

# Main Application DB
db_client = DatabaseClient(
    name="main",
    database_url=settings.database_url,
    echo=False
)

# OMOP CDM Vocabulary Client
omop_client = None
if settings.omop_database_url:
    omop_client = DatabaseClient(
        name="omop",
        database_url=settings.omop_database_url,
        echo=True
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("="*60)
    logger.info(f"{app.title} Starting")
    logger.info(f"Version {app.version}")
    logger.info("="*60)
    
    logger.info(f"Checking main database...")
    db_client.create_all_tables()
    
    logger.info("Loading seed data...")
    try:
        from api.database.seed_preset_values import seed_all
        
        if settings.force_reseed:
            logger.warning("FORCE_RESEED enabled - will clear and reload data")
        
        db_session = db_client.get_session()
        seed_all(db_session, force_reseed=settings.force_reseed)
        logger.info("Seed data loaded successfully")
        cache = get_preset_cache(db_session)
        logger.info(f"Preset cache initialized with {len(cache)} codes.")
    except FileNotFoundError as e:
        logger.error(f"Lab value preset seed data file not found: {e}")
    except Exception as e:
        logger.error(f"Error loading lab value preset seed data: {e}")
        logger.exception(e)  # Full stack trace
    finally:
        db_client.get_session().close()
    
    logger.info("="*60)
    logger.info("Startup complete")
    logger.info("="*60)

    yield
    
    # Shutdown
    logger.info("="*60)
    logger.info(f"{app.title} Shutting Down")
    logger.info("="*60)

app = FastAPI(
    title = app_title,
    version = app_version,
    lifespan=lifespan
)

if settings.root_path:
    app.root_path = settings.root_path

# Add secondary routers
app.include_router(presets_router.router)
app.include_router(samples_router.router)
if omop_client is not None:
    app.include_router(terminology_router.router)

# Add Security Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    if request.url.scheme == 'https':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# Setup Logging
setup_logging(log_level=settings.log_level, show_fhirsheets_logs=settings.show_fhirsheets_logs)



"""
Provides basic information about the application.
"""
@app.get("/info", response_class=PrettyJSONResponse)
async def info():
    if omop_client is None:
        terminology_search_status = "Disabled (Client not configured)"
    else:
        terminology_search_status = "Enabled"
    return InfoResponse.model_validate({
            "application": app.title,
            "version": app.version,
            "features": {
                "terminologySearch": terminology_search_status
            }
        }) 


"""
Returns use cases/scenarios.
"""
@app.get("/usecaseguidance", response_class=PrettyJSONResponse) # LEGACY SUPPORT ONLY
@app.get("/scenarios", response_class=PrettyJSONResponse)
async def get_use_case_guidance():
    use_cases = read_use_case_assets()
    return UseCaseCollectionResponse.model_validate({
            "count": len(use_cases),
            "useCases": use_cases    
    })


"""
Generate FHIR Output
"""
@app.post("/generate", response_class=PrettyJSONResponse)
async def generate_fhir(cohort_settings: CohortSettings, raw: bool = False):
    # Execute Generation using settings and build the FHIR Sheets Inputs.
    resource_definitions, resource_links, cohort = start_generation(cohort_settings, settings.iteration_limit)

    # Setup FHIR SHeets configuration.
    fhir_sheets_config = FhirSheetsConfiguration({"random_seed": cohort_settings.seed})

    if cohort_settings.output_format == OutputFormat.JSON:
        # TODO: Current version of this keeps flow from original implementation to avoid breaking changes. Needs to be handled in like manner to NDJSON once ready.
        bundle_list: list[Bundle] = []
        try:
            for i in range(cohort_settings.count):
                bundle_dict = create_transaction_bundle(resource_definitions, resource_links, cohort, i, fhir_sheets_config) # pyright: ignore[reportUnknownVariableType]
                bundle = Bundle.model_validate(bundle_dict)
                bundle_list.append(bundle)
        except Exception:
            raise HTTPException(status_code=500, detail="Something went wrong executing FHIR generation library.")
        if raw:
            return package_contents_as_json(bundle_list, cohort_settings)
        else:
            return package_contents_as_binary(bundle_list, cohort_settings)
    elif cohort_settings.output_format == OutputFormat.NDJSON:
        record_list: list[list[FHIRResource]] = []

        try:
            for i in range(cohort_settings.count):
                patient_record_raw = create_resources(resource_definitions, resource_links, cohort, i, fhir_sheets_config) # pyright: ignore[reportUnknownVariableType]
                patient_record: list[FHIRResource] = [FHIRResource(**resource) for resource in patient_record_raw.values()] # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                record_list.append(patient_record)
        except Exception:
            raise HTTPException(status_code=500, detail="Something went wrong executing FHIR generation library.")

        return package_contents_as_ndjson(record_list, cohort_settings)
    else:
        raise HTTPException(status_code=501, detail="Output type not implemented. Please see documentation for supported output types.")

"""
Convert Summary to CSV
This takes back in a generation summary from the UI and converts it to a CSV. As the generation is not saved in memory, there
is no way to make this generate without feeding the data back in. In future versions with a generation history, this can be changed.
"""
@app.post("/convert-summary-to-csv")
async def export_to_csv(summaries: List[PatientContainer]) -> StreamingResponse:
    """
    Accepts a list of PatientRecordSummary objects and returns a CSV file.
    Handles dynamic resourceCounts keys.
    """
    # Create an in-memory text stream
    output = io.StringIO()
    
    # Flatten the data
    flattened_data = []
    all_resource_types = set()  # Collect all possible resource types
    
    # First pass: flatten data and collect all resource types
    for container in summaries:
        summary = container.summary
        row = {
            "Name": summary.name,
            "Birth Date": summary.birth_date,
            "Sex": summary.sex,
        }
        
        # Add resource counts with " Count" suffix
        for resource_type, count in summary.resource_counts.items():
            column_name = f"{resource_type} Count"
            row[column_name] = count
            all_resource_types.add(column_name)
        
        flattened_data.append(row)
    
    # Create ordered fieldnames: basic fields first, then sorted resource counts
    basic_fields = ["Name", "Birth Date", "Sex"]
    resource_fields = sorted(all_resource_types)
    fieldnames = basic_fields + resource_fields
    
    # Write to CSV
    if flattened_data:
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(flattened_data)
    
    # Reset the stream position to the beginning
    output.seek(0)
    
    # Return as a streaming response
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=patient_summary.csv"
        }
    )
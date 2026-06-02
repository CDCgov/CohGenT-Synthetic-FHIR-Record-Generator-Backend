# Changelog

## [Unreleased]
### Added
* Valueset Feature
  * Valueset feature added. This feature is used to serve special valuesets to the UI that are expected to be relatively static and are not standard in OMOP CDM databases. For example, UCUM measurements. Valuesets are loaded into the database on startup as part of seed data. For this release, each valueset is considered "unique" and has its own endpoint. Eventually valuesets will be (or should be) migrated to a reusable pattern.
  * U.S. Federal Tribal Affiliation valueset added.
* Added support for arbitrary extensions in use case/scenarios.
  * New field type, "Extension" (case sensitive).
  * "Extension" has an additional `extensionDetails` field which is required if type is Extension. The `extensionDetails` field defines both the extension's value\[x\] type as well as the extension's FHIR URI.
  * NOTE: Arbitrary sub extensions not currently supported.
### Changed
* "Force Reseed" option now also applies to valuesets (and will apply to all other seeded data as well).


## [1.0.2] -  - Minor Feature Addition and Fixes
Note: Version aligned with UI release.
### Added
* Enhanced terminology search with preset availability indicators. Search results now include a `hasPresets` field showing which concepts have predefined value ranges available. Implemented with in-memory caching that automatically updates when presets are added or removed.
* Update samples endpoint now added. `PUT /samples/{id}` with a body of the settings. Note: This can overwrite any existing sample so should be used with caution. There are currently no safeguards in place.
* Patient telecom (ContactPoint[] type) is now supported. Generates both email and phone number for each patient. IMPORTANT: For this release, masking values is not handled. A future version will shift "masking" to all major PII instead of just name. Additional control will also be added for chance to occur for each telecom contact point to support more variety in data. Assumes special value of $patientContactPoint.
### Fixed
* Sample settings now return properly as JSON rather than a string that must be parsed.
* Several points of inconsistent error handling fixed.
* 
### Changed
* Several points of error handling, including logging and reporting to clients, have been improved. More to follow.
* All database tables swapped to using more modern mapped columns in SQL Alchemy.
* To support realistic emails, patient names are now generated as part of initial setup for patient meta information, and then when the human name is processed it will pull from the patient_meta.name field or set the value for FHIR sheets as "masked" depending on settings. This will eventually be further modified to support processing of name for practitioners/etc.
* MedicationRequest.intent changed to "order" (was "plan").

## [1.0.0] - 2026-05-08 - Release 1
### Added
* Basic security related headers now included in API responses.
* "Allowed CORS origins" now configurable from the dotenv file.

## [0.2.3] - 2026-04-17 - Minor Feature Additions
### Added
* `/samples` endpoint is now active. Supports GET to retrieve all samples or POST to create a new sample. The post body assumes the settings built by the UI with an appropriate metadata field. This is *not* for a use case/scenario file directly, it is for cohort settings.
* Added reusable radiology report entity based on US Core 6.1.0 Diagnostic Report Note profile.
* Support for NDJSON (Bulk FHIR) output is now functional. Options are "JSON" or "NDJSON". XML not yet supported.
* Lab value preset table is now populated on startup. If the table needs to be recreated based on the CSV (provided in the /data folder) due to errors or additions, the FORCE_RESEED environment variable may be set to "True". Warning: If you add rows to the database directly without adding them to the seed file, this will cause that data to be lost on a restart. It is strongly recommended to back up any additions to the data or add them to the seed file directly.
* `POST /convert-summary-csv` is now live which converts a summary from a generation run into a CSV file. As the original generation is not kept in memory, the summary must be fed back into the API.
### Changed
* "Condition Clinical Status" is now a special field and filled in based on whether or not an abatement date is present.
### Fixed
* Due to the change in how clinical status is managed, issues with FHIR validation due to misaligned status and abatement has been solved.

## [0.2.2] - 2026-04-02 - Major validation alignment and additional configuration options 
### Added
* Added Use Case Version, FHIR Version, and US Core Version to use case files for handling multiple versions of the same use case scenario as described by those fields.
* Added equivalent fields for FHIR Version and US Core version in cohort settings. Note that FHIR Version defaults to R4 and Use Core Version is optional.
* Added configurable "iteration limit" for event set repetition to avoid unmanagable amounts of generation.
* Condition Based Record Use Case
  * Added entity for US Core Encounter. This entity assumes generic coding of Ambulatory and the basic Snomed "Encounter Procedure" code.
* Entities may now declare additional reference paths. (E.g., PrimaryEncounter --reasonReference--> PrimaryCondition) via the "otherReferences" key.
* Added support for boolean FHIR type. Currently only supports static values and weighted strings. Requires field in entity model to include the new boolean map object which will connect any number of strings to true or false values.
* Added full location handling. Street address is always randomized. If no city or state is provided they are randomized. Attempts to get a valid zip code from 2 letter state code, but if fails will fall back to a random zip code. No county is given, country is always U.S.
* README has had several key sections added to it. Still a WIP.
* Added configuration option to disable run logs due to size. (`enable_run_logs: bool`)
* Terminology search now supports POSTs with the same parameters as a json object. (GET is still supported as well.)
### Changed
* GenerationSummary "date" swapped to str type to provide ISO formatted string with timezone information.
* Generation time is now explicitly timezone aware and always UTC
* Generation "Count" now is restricted to between 1 and 50
* In Condition Based Record use case
  * swapped order of clinical data and medication
  * "condition abatement" was reframed to "condition duration"
  * medication and clinical data step order swapped
* References to "CodeableConcept" have been shifted to "Coding". Handling of "CodeableConcept" was added on top of this to be synonomous with Coding While Cohgent is targeted towards the FHIR Sheets interface and not directly aligned with FHIR naming conventions, this was done to reflect that both types must be handled regardless and that it is more accurate to say that FHIR Sheets handles CodeableConcepts like Coding, than Coding like CodeableConcepts. This leaves Cohgent with a "Coding first" approach, in which the input to generate a CodeableConcept in the final FHIR output is the Coding type. (Yes, I know this is confusing and I apologize. The naming in the FHIR Specification itself makes this difficult to discuss clearly.)
### Fixed
* Typo fixed in condition preset list for "Syphilis (disorder)"
* Fixed CodeableConcept (now Coding) to allow all fields to be optional (still needs more complex validation)
* Fixed CodeableConcept (now Coding) type handler to not send None values to the library
* Fixed CodeableConcept (now Coding) validation (now requires either code or display, and if no code always sets system to None)
* 2.4.6 FHIR Sheets update solves empty strings in Codings and issues with reasonReference field in Encounter.
* Numerous areas of code cleanup, added comments, resolved TODOs, etc.

## [0.2.1] Bug fixes and minor improvements - 2026-03-11
### Added
* Added a filter for invalid codes to the Terminology Search.
* Added support for "instant" type in type handler. (Just passes it off to the current dateTime function which is instant compliant.)
### Changed
* Changed search term criteria in Terminology Search to "and" instead of "or"
* Changed label in Condition Based Record use case/scenario from "Condition Code" to "Condition Concept" to avoid redundancy and improve labeling.
### Fixed
* Base Dockerimage swapped to non-slim version to better handle some environments.
* Updated psyocopg[binary] dependency to use correct packaging (changed from psycopg-binary)
* U.S. Core Diagnostic Report 6.1.0 Lab Entity
  * Added "DiagnosticReport.issued"
  * Fixed category display to "Laboratory"
* Additional Entity handling for "code" fields is no longer tied to only Observation. For now, as only Observation and Procedure are supported and both follow the same pattern ("{ResourceType}.code") the handling has been swapped out to match to if the field ends with ".code". This is a temporary solution until priorities can be established with additional resource types or fields which may be codeableConcepts.
### Dependencies
* Updated fhir-sheets to 2.3.0 (this should address handling of unknown OMB race)
* Subsequent update to fhir-sheets to 2.3.1 (addresses empty objects and handling of "instant" type)

## [0.2.0] - 2026-03-05
### Added
* Added Database Client
* Added Terminology Search Endpoint (Search against OMOP Database Concept table) (See Swagger Docs)
* Observation (Measurement) Value Preset Endpoints
  * Search Observation Value Presets by Code + System (See Swagger Docs)
  * Create Observation Value Preset (See Swagger Docs)
  * Delete Observation Value Preset (See Swagger Docs)
* Added env configuration for `ROOT_PATH`, allows .env handling for Fast API Root Path. Set to non base deployment path, e.g. "/cohgentapi". Solves issues with Swagger not loading.
### Changed
* Countless things, too many to list.
### Fixed
* Numerous minor bug fixes.
* Error handling for FHIR-SHEETS bundles which are not json serializable (will skip those bundles when generating JSON files for the ZIP).
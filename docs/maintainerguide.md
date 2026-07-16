# Information for Contributors and Maintainers

This section of the documentation discusses a number of core design aspects for the CohGenT backend service intended for open source contributors and codebase maintainers.

## Overview

CohGenT is a "model-forward" synthetic patient cohort generator, intended to provide diversified testing data in alignment with a defined "Use Case Scenario". (Note: "Use Case Scenarios" are broadly equivalent to Synthea Modules.) "Use Case Scenarios" define a set of entities (models) representing abstractions of FHIR Resources with additional information used to guide data generation. It is an expansion of the entity model defined by the FHIR Sheets CLI tool. 

The following are common defintions used throughout CohGenT.

- Use Case Scenario - Use case scenarios are as JSON/JSON5 file that contains the information needed to generate a patient cohort. They include models defining the entities which are built into FHIR Resources, instructions on what common models (which exist outside of the use case scenario file) can be used, and instructions for the user interface on how to build a form to configure parameters for the cohort. Use case scenarios are the backbone of all generation.

- Cohort Settings/User Responses - Cohort Settings are end user provided information, typically provided as a submission through the form rendered in the user interface, based on a use case scenario file. This includes settings for specific fields like patient demographic distributions, what additional data should be added, and meta settings such as patient count to generate. (Note that the use case scenario itself should include defaults for any use configured options, which both informs the user interface's default state as well as provides a fallback if missing from the cohort settings) **(NOTE: "Cohort Settings" in the UI also refers to the form state which may be saved and loaded. This is a distinct entity from the cohort settings class ingested by the API.)**

- Entity - An entity is an object modelings the fields that will be generated into a FHIR Resource, as well as meta data (labels, resourceType, etc.) Each use case scenario should include all core and unique entities related to it. Entities setup within the use case scenario directly are considered singletons and are only generated one time per patient in the cohort. This includes the patient resource itself. What consitutes an entity to be included depends entirely on the use case scenario. For example, the basic "condition based record" scenario includes the Patient, a Condition, and an Encounter as central to the record. These are non-reusable and tailored to the needs of that specific use case scenario.

- "Common" Entity - Common entities are entities that exist in isolation as their own file, and may be reused across any number of use case scenarios. For example, basic lab results. Common entities can be configured to generate repeatedly. In the context of the "condition based record", this would be repeat labs, medications, and other data that is more dynamic than the core use case scenario entities. While the divide isn't explicitly a matter of generating one or many resources, this is likely often the case. Which common entities should be used are configured in the use case scenario file under the `commonEntities` model. NOTE: Not all use case scenarios require common entities. Certain, complex snapshot records, such as a death certificate, may be made up entirely of entities inside the main use case scenario, as needs such as lab monitoring do not exist.

- Event Period and Primary Event Date - When configuring the parameters for generation through Cohort Settings, an event period is defined. This is the date range for the primary event (the core inclusion criteria in a real study) may occur. For example, "Tuberculosis diagnosis between 2005 and 2010" might be an inclusion criteria in a real world cohort, which would translate into an event period of Jan 1 2005 through Dec 31 2010. In the basic Condition Based Record use case, Tuberculosis would then be set as the Primary Condition defined by that use case scenario. When generation occcurs, each patient is then assigned a random "event date" within that event period for that primary condition onset/diagnosis, mimicking a selection of patients in a real world cohort who had a diagnosis of Tuberculosis in a given date range.

- "Clinical Data Sets"/"Event Sets" - Clinical Data Sets, originally called Event Sets, are groups of clinical data (events) that make up the bulk of a patietn record, such as lab tests and procedures. These are often repetitive events that occur over the course of an episode. For example, bi-weekly lab draws or imaging. Each item in a clinical data set uses a common entity as a template. A set can have a timing assigned relative to a patient's primary event date, including offset (e.g., starting 1 week after diagnosis), if and how often the clinical event repeats (e.g., every 2 weeks), and when generation should stop (e.g., at the end of the cohort or patient level generation period, or at a time specific to that set such as "for 3 months").

## Repository and Source Code Layout

The repository is laid out as follows:

* `./` - The project root. Includes the main README, CHANGELOG, disclaimer, licenses, Docker related artifacts, environment files (`.env`) and a few helper scripts.
* `./api/` - The main source code root folder.
* `./docs/` - Documentation.
* `./data/` - Seed data that is loaded on initial launch of the API
* `./logs/` - Where all run logs and error logs may found. (Only created once logs are first gathered.)
* `./tests/` - Unit tests, etc.

The source code within the `./api/` folder includes the following modules:
* `./api/main.py` - The entry point for the FastAPI services, including some main endpoints. (Many narrower features have their own router files.)
* `./api/assets/` - Static assets read from the disk during run time.
* `./api/database/` - The main database client as its own module along with SQL Alchemy table files.
* `./api/features/` - The main features organizational folder, most code falls under here.
* `./api/features/generation/` - Anything related to data generation. (Excluding the FastAPI router.)
* `./api/features/presets/` - Anything related to serving observation value presets. (Excluding the FastAPI router.)
* `./api/features/terminologysearch/` - Anything related to the OMOP Database Terminology Search. (Excluding the FastAPI router.)
* `./api/models/` - Core application Pydantic models and some small Python helper classes for typing. This is where you can find things such as the Use Case Scenario model or the Cohort Settings model. It includes several sub folders for specific groups of models, such as type hint oriented FHIR models (mostly AI generated as they are just for type hinting and not structurally important), and API requests and responses.
* `./api/routers/` - All FastAPI router files. Generally there is one per feature. Note that some simpler features may consist of only the router file.
* `./api/utilities/` - A catch all for helpers and services that don't fall entirely within a specific feature scope, such as the final output formatter.

## API Documentation

FastAPI will automatically generate Swagger docs at the server `/docs/` path. For example: `http://localhost:8000/docs`. These docs will provide an overview of all available endpoints and Pydantic models.

## General Application Stack Workflow

**Phase 1: Initial Setup & Use Case Loading**
1. UI Startup → Fetches available use cases from API
2. API → Returns use case list with metadata
3. User → Selects a use case (e.g., "condition-based-record")
4. UI → Requests full use case definition from API
5. API → Returns use case JSON with:
  * Entity definitions
  * Form rules
  * Default settings
  * Common entity references

**Phase 2: Form Generation & User Configuration**
1. UI → Parses form rules and renders dynamic form
2. User → Configures parameters:
  * Patient count
  * Seed
  * Event period (start/end/until dates)
  * Demographic distributions (gender/race/ethnicity weights)
  * Clinical data (event sets, medications, etc.)
3. UI → Validates input and builds CohortSettings object

**Phase 3: Generation Request**
1. UI → POSTs CohortSettings to /generate endpoint
2. API → Receives and validates CohortSettings
3. API → Calls start_generation()

**Phase 4: Data Generation (Backend)**
1. Generation Module:
  * Parse use case & default settings
  * Generate entities
  * Setup patient distributions
  * For each patient:
    * Generate demographics
    * Process static entities
    * Generate event sets (repeating clinical data)
    * Process medications
    * Build patient row dict
2. FHIR Sheets Interface → Convert to resource definitions/links
3. FHIR Sheets Library → Generate FHIR Resources
4. Output Formatter → Package as JSON bundles or NDJSON + create zip

**Phase 5: Response & Download**
1. API → Returns GenerationSummary with:
  * Timestamp
  * Generation parameters
  * Patient summaries (name, birthdate, resource counts)
  * Base64 encoded zip file
2. UI → Decodes and presents:
  * Summary table of generated patients
  * Download button for zip file
3. User → Downloads synthetic FHIR data

## Models

NOTE: Most classes in this application are built out as Pydantic models. Additionally, many use either CamelModel or NoNullCamelModel as their base. CamelModel is a Pydantic extension that automatically serializes Pythonic snake case (`some_field`) into JSON standard camel case (`someField`) to be friendlier to the UI. The NoNullCamelModel further extends this to exclude "None" values from being returned in API responses, as the behavior was inconsistent without adding the extra layer of explicit serialization. Generally, there is no reason not to just use NoNullCamelModel, though many artifacts still use originally setup BaseModel or CamelModel where it was not problematic, as a full across the codebase update was deemed unimportant. 

### Use Case Scenarios

A "Use Case Scenario" is a specific public health/clinical scenario represented as a set of discrete entities along with associated end user facing form controls to guide generation of a patient cohort as FHIR. Entities consist of fields which can be populated with static values through direct assignment in the entity model or linked to the form controls to allow end user configuration. (Entities will be discussed in more depth below.)

The Use Case Scenario file can be either JSON or JSON5 (JSON with comments).

Relevant Files:
* `./api/models/use_case.py`

### Entities and Fields

An "Entity" models the backbone of a FHIR Resource (e.g., `Patient`) for generation, defining meta data such as an identifier for the Entity, the Entity's profile, major references/links to other Entities, and the Fields within. A "Field" is a single FHIR Resource field (e.g., a patient's name). Each Field provides information on the FHIR Path for the (FHIR) field within the resource (e.g., `Patient.name`), the FHIR type, whether or not the Field is use configurable in the current use case, and if not user configurable what the value should be set as. For user configurable fields, it also includes which user control ("Option") it connects to via the `userSettingRuleId` attribute, and may contain special map objects that connect the user facing options to a specific value such as a boolean or Coding based on the FHIR Type of the field.

For example, given the case of the `Patient.deceasedBoolean` field, the user facing UI option may provide a weighted binary option of either "Living" or "Deceased". Using the `booleanMap` attribute, "Living" can be mapped to False and "Deceased" to True when generating the FHIR output.

Entities support inheritance through the `baseEntity` attribute, allowing common field sets to be reused across similar resources (e.g., base observation fields shared by multiple lab test entities).

Relevant Files:
* `api/models/entity.py`
* `api/models/field.py`

### Form Rules

Form Rules define the user interface controls for configuring cohort generation parameters. Each use case scenario includes a `formRules` array that specifies the form structure, including organization into steps/sections and the individual configuration options presented to users. This is a simplified approach based on FHIR Questionnaires.

**Form Structure:**
- **Steps**: Organize the form into logical sections (e.g., "Patient Demographics", "Clinical Data"). Each step has a label and contains multiple options. Steps may either be defined purely by the use case scenario by defining the type as `custom` or leverage one of the prebuilt UI steps for common needs.
- **Options**: Individual configuration controls within a step. Each option is defined by the `Option` model, which specifies the control type, labels, default values, and validation rules.

**Supported Control Types:**
Options can use various control types to match the data being configured:
- `CHECKBOX` - Binary on/off toggles (e.g., "Include smoking status")
- `RANGE` - Numeric ranges with min/max (e.g., patient age 20-65)
- `WEIGHTING` - Distribution sliders for weighted selections (e.g., 40% male, 60% female)
- `RELATIVE_TIME_RANGE` - Time offsets in days (e.g., onset 30-90 days before event)
- `TRIBAL_AFFILIATION` - Tribal affiliation selector with prevalence
- `OCCUPATION` - Occupation code selector
- `CONCEPT` - Clinical concept/terminology picker (codes, diagnoses)
- `LOCATION` - Geographic location (state, city)
- `PREVALENCE` - Prevalence-based controls for optional features

**Connecting to Entity Fields:**
Options connect to entity fields through the `ruleId` attribute in the Option and the `userSettingRuleId` attribute in the Field. When a field is user-configurable (`userConfigured: true`), its `userSettingRuleId` must match a `ruleId` from an option in the form rules. During generation, the system looks up the user's setting for that rule ID and applies it to the corresponding field.

**Example:**
```json
// In formRules
{
  "ruleId": "patient-age",
  "label": "Patient Age Range",
  "control": "range",
  "defaultValues": [18, 65]
}

// In entity field
{
  "path": "Patient.birthDate",
  "userConfigured": true,
  "userSettingRuleId": "patient-age"
}
```

When generation occurs, the user's age range setting (retrieved via `ruleId: "patient-age"`) is used to calculate appropriate birth dates for the `Patient.birthDate` field.

Relevant Files:
* `api/models/use_case.py` - FormRule model
* `api/models/option.py` - Option and ControlType definitions
* `api/models/cohort_settings.py` - Setting model (user responses)


### Common Entities

Common entities are reusable entity templates stored as separate files in `./api/assets/commonentities/` that can be shared across multiple use case scenarios as part of the `additional-data-time-series` form step, which connects to (user facing in the UI) Clinical Data Sets or (in the API model) Event Sets. Unlike the singleton entities defined directly in a use case scenario file, common entities are designed to be generated multiple times (e.g., lab results that repeat weekly) and which of the templates are used may be customized per use case.

**Why Common Entities?**
Common entities solve the problem of repetitive entities for large amounts of data generation over an extended period. For example, lab observations follow the same FHIR structure regardless of which specific lab test is being ordered and in which context (defined as the use case scenario) it is being ordered. Rather than defining a complete Observation entity for every possible lab test in every use case, you create one "US Core Observation Lab" common entity template and reuse it with different lab codes (LOINC codes) specified in each use case in the `additional-data-time-series` step of the UI (shown as Clinical Data). 

**Structure:**
Common entity files contain standard Entity definitions just like entities in use case scenarios, but they're designed to be:
1. **Reusable** - The same entity file can be referenced by multiple use cases
2. **Parameterizable** - Key fields (like diagnostic codes) can be overridden when referenced
3. **Repeatable** - Used in event sets to generate multiple instances with different dates/values
4. **Dynamically linkable** - Can reference provider entities or use case entities through dynamic references

**How to Use Common Entities:**

1. **Reference in Use Case** - In your use case scenario's `commonEntities` section, specify which common entity files to use:
```json
"commonEntities": {
    "diagnosticReport": "USCoreDiagnosticReportLab",
    "medication": "USCoreMedicationRequest",
    "additionalEntities": [
        {
            "entityId": "labResult",
            "type": "observation",
            "buttonLabel": "Lab Result",
            "entityFile": "USCoreObservationLab",
            "defaultSystem": "LOINC"
        }
    ]
}
```

2. **Use in Event Sets** - Reference the common entity by its `type` when defining repeating clinical data:
```json
"eventSets": [
    {
        "name": "Weekly Labs",
        "timing": {
            "offset": 0,
            "repeat": true,
            "repeatTiming": 7
        },
        "entry": [
            {
                "type": "observation",  // matches additionalEntities.type above
                "codeableConcept": {
                    "system": "http://loinc.org",
                    "code": "2823-3",
                    "display": "Potassium"
                }
            }
        ]
    }
]
```

3. **Configure Dynamic Links** - Common entities can include `dynamicReferences` that get resolved when used. This allows linking to provider entities or other resources specific to each use case. See the "Dynamic References" section for details on how these links work.

**Built-in Common Entities:**
- `USCoreObservationLab` - Lab test results
- `USCoreDiagnosticReportLab` - Lab report containers (configured at the event set level to wrap a set of lab test observations)
- `USCoreDiagnosticReportRadiology` - Radiology reports  
- `USCoreProcedure` - Clinical procedures
- `USCoreMedicationRequest` - Medication orders (handled in their own step outsode of `additional-data-time-series`/Clinical Data but in a similar way)

**Creating New Common Entities:**
1. Create a JSON file in `./api/assets/commonentities/`
2. Define the entity following the standard Entity model structure
3. Use `dynamicReferences` for any links that should be configurable per use case
4. Add user-configurable fields where appropriate (e.g., observation values)
5. Reference it in use case scenarios via `commonEntities.additionalEntities`

Relevant Files:
* `./api/assets/commonentities/` - Common entity definition files
* `./api/models/use_case.py` - CommonEntities and AdditionalEntity models
* `./api/utilities/file_reader.py` - `read_common_entity()` function


## Type Support
FHIR Type support is limited in the current version of the application, based around what was defined for the existing scenario(s). Typing is a complex alignment between the user input, the generation requirements, and the expected FHIR Sheets formatting. For example, the internal typing provides for a "ValueCoding" type in Pydantic which handles a combination of system, code, and display strings and is allowed input to generate either the FHIR Coding or CodeableConcept types. When building or modifying a scenario, failure to align allowed input types to the FHIR type will cause an error in processing.

Currently the following combinations are supported:
| CohGenT Input Type | FHIR Output Type | Notes
|-------------|------|------
ValueAddress | Address | Only supports setting State and City. Country is always US. Other elements are always randomized.
ValueCoding | CodeableConcept | Only a single Coding element is supported.
ValueCoding | Coding
ValueOccupation | CodeableConcept | Special field that will compare a code against the occupation table of the database.
ValueRangeWithUnits | Quantity | Observations only.
ValueTimeRangeAsDays | datetime | Generates a relative datetime based on generation parameters.
ValueTimeRangeAsDays | instant | Generates a relative datetime based on generation parameters.
ValueWeights (with boolean map field) | boolean
ValueWeights (with concept map field) | CodeableConcept
ValueWeights (with concept map field) | Coding
ValueWeights | string | Observations only.

Note that "HumanName" is a special field and considered always randomly generate (though in more static locations like provider entities, can be defined by its sub elements). For more information, see the special values listed further down. (For preset static names, use FHIR Sheets style indexing. This is mostly only applicable to static provider resources.)

Static field values may be defined in the entity definitions for fixed values in FHIR profiles mostly, but also for non-user facing concerns such as Observation statuses. The supported types are:
* ValueCoding -> Coding
* ValueCoding -> CodeableConcept
* string -> string
* string -> code
* string -> Address (in FHIR Sheets carat delimited format)
* string -> CodeableConcept (in FHIR Sheets carat delimited format)
* string -> Coding (in FHIR Sheets carat delimited format)

Special values can be used for some fields, set as a reserved string. These direct generation.
* $uuid - Used for Identifier fields to note that a UUID should be inserted.
* $patientName - Used only for the name (HumanName type) field in a Patient resource to note where a name (or a data absent reason) should be inserted.
* $eventDate - Set a datetime field to match the generated event date for a patient (the central date in a patient's record to which all other dates are relative)
* $current - Set a datetime field as the current datetime being iterated through in cases where repetition is occuring. For example, when there are repeat lab tests in an event set that generate weekly, specifying $current will appropriately fill in the blank with the date of the current iteration relative to the event date. This should only be use for entities which can repeat.
* $conditionClinicalStatus - Set either "active" or "resolved" for a Condition resource dynamically by whether an abatement date setting exists. This simply checks if there is a default or user provided setting with a path starting with "Condition.abatementDate" in the entity, and then evaluates if it will produce a date (start and end date of the relative time range are not 0, which for that type indicates a "do not generate" empty state). Note that this should only be used with Condition.clinicalStatus. There is no validation enforcing this however. In future versions this would ideally be changed to a more generic rule handling.
* $patientContactPoint - Sets both email and phone systems with values.
* $industry - Sets the patient's industry relative to occupation. **WARNING: Must come after occupation in the field order. ODH UsualWork profile only.**

Some other special values ($) are present but do not have special functions attached to them, and are only to meet validation requirements for certain user configured fields. These should be disregarded.

## Generation Module
The Generation Module is an internal component which provides the actual data generation for a given set of user settings and scenario. The output of the Generation Module are the FHIR Sheets input models, which are representative of a spreadsheet input processed by the FHIR Sheets library. Entities are defined external to the main "table" (in a specific page of a spreadsheet in the CLI version of FHIR Sheets), while each "column" in the main table is a single field within an entity. For example, the entity definitions will lay out something like the "US Core 6.1.0 Patient" profile, while a single column in the main data table will be the `Patient.birthdate` field for that entity.

### Special Fields
While most fields are intended to be handled dynamically, there are a few important exceptions. Foremost among these are the primary event date for a given patient, the patient's name, the patient's gender (`Patient.gender`), and the demographic distributions for all patients. Primary event date is used to set the baseline date for all of the patient's records. Gender is used as a depedency to generate names.

### Resource References
References in FHIR provide a link between Resources, such as indicating the subject (patient) of an Observation or the clinician who diagnosed a Condition.

In CohGenT, references can be defined one of several ways:
* Direct subject reference
* Static Reference
* Dynamic Reference

#### Direct Subject Reference

For every resource which has a main subject/patient reference, this is defined specifically in the entity model by the `referencePath` field, and always points to the use case scenarios `PrimaryPatient` entity. For most resources, this is simply `subject` (the resource type is not required as with other FHIR Paths).

For the example below, the Condition resource uses the subject field.
```
{
    "abstract": false,
    "entityId": "PrimaryCondition",
    "resourceType": "Condition",
    "profile": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis",
    "referencePath": "subject",
    "fields": [ ... ]
}
```

#### Static Entities

Additional references to other entities may be defined in the `staticReferences` or the `dynamicReferences` fields. Static References are direct references defined within a single use case scenario.

Static References is a simple list of objects including `referencePath` and `targetEntity` (the entity the reference should be to).

For example, in the Condition Based Record scenario, the PrimaryEncounter entity (U.S. Core Encounter profile) includes a `reasonReference` to the PrimaryCondtion (U.S. Core Encounter Diagnosis Condition profile) as shown in addition to it's primary subject/patient reference:
```
            "referencePath": "subject",
            "staticReferences": [
                {
                    "referencePath": "reasonReference",
                    "targetEntity": "PrimaryCondition"
                }
            ],
```
This will creat a reference in the FHIR output from the Encounter to the Condition resources in question.

Note that entities defined this way are non-repeating, and so further configuration of references is not required.

#### Dynamic References
Dynamic references are defined within common entities that exist outside the use case scenario, such as lab or radiology entity templates, which allow more customization to meet the needs of many use cases. 

>**NOTE:** Dynamic References set in the main use case scenario entities will not be parsed. Those entities should be built into the use case scenario directly. Dynamic References are only parsed for common entities used in clinical data sets, as these exist outside of the use case.

The DynamicReferences field is only (currently) used in secondary entity templates, which can be referenced in any number of use case scenarios for additional entity generation. For example, lab result observations. Here the field includes the path to use for the reference as with static references, but instead of actually pointing to a specific entity (as no other entities exist within its direct context) has a `linkIdentifier`. The `linkIdentifier` can then be referenced in the Additional Entities section of the use case scenario file to connect to an actual entity either from the provider database or within the use case scenario..

The following is an example of the field in the lab observatio common entity:
```
"dynamicReferences": [
    {
        "referencePath": "performer",
        "linkIdentifier": "performer"
    }
],
```
(Note that the matching `referencePath` and `linkIdentifier` for "performer" is incidental.)

This can then be referenced from the use case in the additional entities section like so:
```
{
    "entityId": "labResult",
    "type": "observation",
    "buttonLabel": "Lab Result",
    "entityFile": "USCoreObservationLab",
    "defaultSystem": "LOINC",
    "dynamicReferences": [
        {
            "targetEntityId": "LabPractitioner001",
            "linkIdentifier": "performer"
        }
    ]
},
```
Gere, the `entityFile` key points to our lab observation entity that will be loaded from the external source, while the `dynamicReferences` field specifically references the dynnamic references within that common entity. This particular example points to a provider entity stored in a database through the `targetEntityId`. When encountered, the generator will attempt to load the matching entity and incorporate it into the generated output. This allows a use case to customize which Practitioner related entities are used to match various use case requirements while still leveraging the same entity definition. For example, if you wanted to model a very specific type of provider and load it to the database, you would be able ot reference that here.

Dynamic reference target entity IDs may also reference an entity within the current use case scenario by adding an `@` markup. For the example below, the procedure common entity includes a dynamic reference to provide a reasonReference field (similar to the example we gave previously with Encounters for static references). which can set to reference the primary condition within the use case scenario entities as follows:

```
{
    "targetEntityIdentifier": "@PrimaryCondition",
    "linkIdentifier": "reason"
}
```

#### Special References

For iterative generation, such as repeating lab observations, in Clinical Data Sets/Event Sets there is special handling when a containing DiagnosticReport is enabled (for Lab Panels, specifically the U.S. Core DiagnosticReport Lab Results profile). In this case, the references to the contained member resources are generated automatically.

>**NOTE:** If an entity identifier cannot be found in the database, the system skips and continues to generate the rest of the record.

#### Provider Entity Reference Chaining Explored

In FHIR, PractitionerRole resources often act as a strong link between clinical data, a performer, and an organization. In CohGenT, if dynamic references point to PractitionerRole entities, the system will attempt to automatically handle those common references, chaining to include any connected Organization and Practitioner entities.

How it works:

When a dynamic reference targets a provider entity, the system:

1. Loads the specified provider entity from the provider cache
2. Checks if the entity has staticReferences defined
3. Automatically loads and includes any other (chained) referenced entities
4. Creates the appropriate resource links between all entities

Example of a PractitionerRole entity setup to chain below:

```json
// In the use case dynamic reference, pointing to the PractitionerRole
{
    "targetEntityId": "USCorePractitionerRole002",
    "linkIdentifier": "performer"
}

// In the PractitionerRole provider entity (practitioner_role_lab.json5)
{
    "entityId": "USCorePractitionerRole002",
    "resourceType": "PractitionerRole",
    "staticReferences": [
        {
            "referencePath": "practitioner",
            "targetEntity": "USCorePractitioner002"
        },
        {
            "referencePath": "organization",
            "targetEntity": "USCoreOrganization002"
        }
    ]
}
```
Result: The system automatically includes:

USCorePractitionerRole002 (Lab Technician Role)
USCorePractitioner002 (Lab Technician)
USCoreOrganization002 (Laboratory)

This creates the complete provider context chain without requiring separate references for each entity in the use case scenario.

*Best Practice: Use PractitionerRole for clinical references (performer, participant, etc.) rather than direct Practitioner references, as it provides richer context including the practitioner's role and organization.*

### Masking PII

CohGenT supports providing limited masking of (simulated) Patient Identifying Information such as name, email, and address. This is done using a special `mask-pii` option in a `custom` step of the form. When enabled, the system will attempt to mask or omit all fields labeled with the `"pii": true` attribute in the entity models.

*WARNING: This feature is largely experimental and may not properly handle primitives or specific fields. This is due to lack of FHIR Sheets handling of special FHIR JSON formatting of primitive type fields, which use the key preceeded by an underscore (`_gender`) to allow the insertion of objects such as the Data Absent Reason extension.*

## Other Features
### Lab Value Presets

The API serves presets for common lab value to the UI to improve usability. Presets are identified by a combination of code, system, and preset_name. Each code/system pair may have many preset ranges, such as low, normal, or high clinical ranges. For example, inputting a concept code of 17861-6 (Calcium test), will provide three ranges to select from to autopopulate the form fields for the lab observation value (min value of range, max value of range, and unit).

Lab value presets are maintained as a CSV file in the `./data/` folder of the project, as `./data/lab_value_presets.csv`. To be read properly on startup, this file must be in this location and be a valid CSV with the specified columns as the base version provided. Note that the "label" and "notes" column are for human readability only, and not parsed into the database.

Presets may also be directly managed through the API (read all, create, and delete endpoints are available). For more information please see the API documentation.

The seed CSV file can also be updated to maintain a set of lab preset values across restarts. Whenever the file is updated, the databse must be manually cleared or the FORCE_RESEED variable set to "True". This will delete all existing data in the table and re-populate it from the seed file. **WARNING**: This will cause you to lose all values posted directly through the API which are also not stored in the preset. It is recommended to add any values you wish to maintain to the CSV alongside posting through the API to make them available without restart.

The CSV contains the following columns:
| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `label` | No* | Human-readable name | `Potassium in Serum` |
| `code` | **Yes** | LOINC code for the test | `2823-3` |
| `system` | **Yes** | Code system URL | `http://loinc.org` |
| `preset_name` | **Yes** | Range category | `low`, `normal`, `high` |
| `value_type` | **Yes** | Type of value | `Quantity` or `string` |
| `quantity_min` | No | Minimum value for range | `3.5` |
| `quantity_max` | No | Maximum value for range | `5.0` |
| `quantity_unit` | No | Unit of measurement | `mmol/L` |
| `priority` | No | Display priority (1-4) | `2` |
| `notes` | No* | Clinical notes or context | `Normal adult range` |

\* Not a column in the database, used for documentation in the CSV only.

### Sample Settings

Sample settings for the UI may be loaded to the database. Note that these are **not** the backend/API level CohortSettings, but the form state object saved from the UI itself. Users may create a cohort configuration, save it, and then upload it through the Sample Settings router endpoints (see Swagger Docs!).

### Provider Entities

Provider entities are special entities stored in the main application database and loaded. They have their own router and CRUDS operations. For more information, please see the dynamic references section.

### Special Valuesets

The API provides several specialized endpoints for valuesets that not are not easily represented due to size and sourcing. For this version this includes Tribal Affiliation and Occupational Data. These are all handled by the `valuesets_router.py` file, and stored in dedicated database tables as simple concepts. These valuesets must be maintained when updated

####

## Migrating Versions of FHIR or Implementation Guides

The core CohGenT application code is FHIR version agnostic, and should not need to be modified for the sake of migrating FHIR or IG versions. However, use case scenarios are built to a single specific version of FHIR and/or IG. The Condition Based Record targets FHIR R4 US Core 6.1.0 (and ODH 1.3.0). This file (and other future use cases) is where the migraton would need to occur--though it is recommended to simply create a new version of the use case scenario and tag it appropriately.

The exception here would be for special handlers such as Tribal Affiliation in CohGenT, or the OMB Race and Ethnicity special handlers in FHIR Sheets.

## Known Issues and Limitations

### Original FHIR Sheets Centric Design ("Iterate and Fill")

This project started out as a way to complete spreadsheets in bulk for the FHIR Sheets CLI tool. This meant the original design focused heavily on the idea of
literally filling out a giant table of dat with logical but mostly arbitrary data, without real field interdepencies or complex considerations. The simple "iterate and fill" approach is unsuited for continued evolution of the application as it has evolved, and has created significant tech debt.

### Incomplete Type Handing

FHIR Types and support for various UI control types were implemented on an as needed basis by feature request for the default Condition Based Record use case scenario. While adding new type support is relatively simple in the API, new control types in the UI may take more dedicated effort.

### Limited Testing with Additional Use Cases

All development focused around the relatively simple Condition Based Record (modeled around a basic public health scenario such as a reportable condition) and more complex or varied scenarios were not able to be tested. For FHIR records that would use mostly snap shot documentings using static values or simple weights among concepts (e.g., Medicolegal Death Investiation using the MDI FHIR IG) this would likely work when entities are modeled properly without code modification, but for more complex IG's with more resource nesting, complex compositions, or requirements such as message bundle wrappers significant upgrades would need to made (to FHIR Sheets as well as CohGenT).
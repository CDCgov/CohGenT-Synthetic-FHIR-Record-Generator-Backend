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

### Entities

TODO
- Entity Model

#### Fields

### Form Rules

TODO
- Form Model
- Types of "steps"
- Types of "controls"
- Connecting a form rule to an entity field


### Common Entities

TODO
- Configuring common entities
- Dynamic Links


## Type Support
FHIR Type support is limited in the current version of the application, based around what was defined for the existing scenario(s). Typing is a complex alignment between the user input, the generation requirements, and the expected FHIR Sheets formatting. For example, the internal typing provides for a "ValueCoding" type in Pydantic which handles a combination of system, code, and display strings and is allowed input to generate either the FHIR Coding or CodeableConcept types. When building or modifying a scenario, failure to align allowed input types to the FHIR type will cause an error in processing.

Currently the following combinations are supported:
| CohGenT Input Type | FHIR Output Type | Notes
|-------------|------|------
ValueWeights (with boolean map field) | boolean
ValueWeights | string | Observations only.
ValueTimeRangeAsDays | datetime | Generates a relative datetime based on generation parameters.
ValueTimeRangeAsDays | instant | Generates a relative datetime based on generation parameters.
ValueCoding | CodeableConcept | Only a single Coding element is supported.
ValueCoding | Coding
ValueAddress | Address | Only supports setting State and City. Country is always US. Other elements are always randomized.
ValueRangeWithUnits | Quantity | Observations only.

Note that "HumanName" is a special field and considered always randomly generated. For more information, see the special values listed further down. (For preset static names, use FHIR Sheets style indexing. This is mostly only applicable to static provider resources.)

Static fields may be defined in the entity definitions for fixed values in FHIR profiles mostly, but also for non-user facing concerns such as Observation statuses. The supported types are:
* ValueCoding -> Coding
* ValueCoding -> CodeableConcept
* string -> string
* string -> code

Special values can be used for some fields, set as a reserved string. These direct generation.
* $uuid - Used for Identifier fields to note that a UUID should be inserted.
* $patientName - Used only for the name (HumanName type) field in a Patient resource to note where a name (or a data absent reason) should be inserted.
* $eventDate - Set a datetime field to match the generated event date for a patient (the central date in a patient's record to which all other dates are relative)
* $current - Set a datetime field as the current datetime being iterated through in cases where repetition is occuring. For example, when there are repeat lab tests in an event set that generate weekly, specifying $current will appropriately fill in the blank with the date of the current iteration relative to the event date. This should only be use for entities which can repeat.
* $conditionClinicalStatus - Set either "active" or "resolved" for a Condition resource dynamically by whether an abatement date setting exists. This simply checks if there is a default or user provided setting with a path starting with "Condition.abatementDate" in the entity, and then evaluates if it will produce a date (start and end date of the relative time range are not 0, which for that type indicates a "do not generate" empty state). Note that this should only be used with Condition.clinicalStatus. There is no validation enforcing this however. In future versions this would ideally be changed to a more generic rule handling.
* $patientContactPoint - Sets both email and phone systems with values.

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

TODO (Rewrite an dclarify)

When dynamic references point to provider entities (Practitioner, PractitionerRole, Organization), the system automatically handles reference chaining to include all related resources.

How it works:

When a dynamic reference targets a provider entity, the system:

Loads the specified provider entity from the provider cache
Checks if the entity has staticReferences defined
Automatically loads and includes any referenced entities
Creates the appropriate resource links between all entities
Example: PractitionerRole Reference Chain

PractitionerRole entities typically reference both a Practitioner and an Organization. When you reference a PractitionerRole, all three resources are automatically included:


// In the provider entity (practitioner_role_lab.json5)
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

// In the use case dynamic reference
{
    "targetEntityId": "USCorePractitionerRole002",
    "linkIdentifier": "performer"
}
Result: The system automatically includes:

USCorePractitionerRole002 (Lab Technician Role)
USCorePractitioner002 (Lab Technician)
USCoreOrganization002 (Laboratory)
This creates the complete provider context chain without requiring separate references for each entity.

Best Practice: Use PractitionerRole for clinical references (performer, participant, etc.) rather than direct Practitioner references, as it provides richer context including the practitioner's role and organization.

### Masking PII

TODO

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

TODO

### Provider Entities

TODO*

### Special Valuesets

The API provides several specialized endpoints for valuesets that not are not easily represented due to size and sourcing. For this version this includes Tribal Affiliation and Occupational Data. These are all handled by the `valuesets_router.py` file, and stored in dedicated database tables as simple concepts. These valuesets must be maintained when updated

####

## Migrating Versions of FHIR or Implementation Guides

TODO
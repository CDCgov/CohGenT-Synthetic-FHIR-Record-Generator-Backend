# CohGenT User Guide (DRAFT)

# Introduction

CohGenT (the Cohort Generation Tool), is a software application designed for public health practitioners, including data analysts and FHIR developers in the realm of public health and epidemiology to assist in creating and managing synthetic cohort data. Within CohGenT, "cohorts" are defined groups of synthetic patients following specific exposures or characteristics that influence the development of health outcomes. CohGent reduces the barrier-to-entry to testing applications with FHIR, providing common scenarios and a simple-to-use interface for those who need to create synthetic patient data.

CohGenT generates synthetic data for testing data exchange including testing interoperability workflows such as FHIR query and Bulk FHIR access . Generated data adheres to configurable FHIR profiles, including US Core, and exports can be validated to ensure they meet required FHIR specifications.
Key features of the tool include:
- A user-friendly interface for designing synthetic cohort FHIR data based on common federal guidelines.
- Integrated tooling to generate FHIR JSON bundles ready for testing environments.
- A cohort file that users can share for reuse.
- A flexible, configurable framework that supports a wide range of cohort scenarios for various use cases.

**General User Workflow**
Start by selecting a cohort scenario, entering a name, and setting the primary event period, or the timing of the event. Then configure the cohort through a series of pages, such as demographics, condition, clinical data, and medications. After completing the setup, review the cohort and confirm the settings before finalizing and generating the synthetic patient data files.


**Resources and Profiles Supported (FHIR R4, US Core 6.1.0)**

- US Core Patient (Patient)
- US Core Condition Encounter Diagnosis (Condition)
- US Core MedicationRequest (MedicationRequest)
- US Core Laboratory Result Observation (Observation)
- US Core Procedure (Procedure)
- US Core DiagnosticReport Profile for Laboratory Results Reporting (DiagnosticReport)
- US Core Encounter (Encounter)
- US Core DiagnosticReport Profile for Report and Note Exchange (DiagnosticReport)
- US Core Organization (Organization)
- US Core Practitioner (Practitioner)

> Note: While US Core Organization and US Core Practitioner are supported by the system, they are not independently generated. They are automatically constructed and included as supporting resources derived from the references present within the primary clinical payloads (e.g., Encounters, Diagnostics, and Procedures).

## Key Features

- A user-friendly interface for designing synthetic cohort FHIR data based on common federal guidelines.
- Built-in generation tooling for creating FHIR JSON and Bulk FHIR NDJSON bundles ready for upload to test services.
- A cohort file that users can share for reuse.
- Configurable and flexible scenario model allowing for development and incorporation of many different cohort scenarios for various use cases.

## Expected Cohort Variation
As a synthetic data generator, CohGenT randomly generates data based on user parameters set.
**Variation in the synthetic data will occur in:**
- Demographics
- Dates and Time Periods of the cohort (provides framing for all other dates)
- Condition Duration
- Frequency and timing of events (Observations/Procedures/Diagnostic Reports)
- Observation Values
- Medications

**Variation in the synthetic data will not occur in the following:**
- The presence of a Resource (e.g., whether or not a medication exists)
- Singular concepts - the code for a specific observation (e.g., a particular lab test, a condition, etc.)

### Other Considerations

- The optimal screen size for using CohGenT is between 1366 x 768 and 1980 x 1080. 
 
## Primary User Actions

The CohGenT home page provides a concise description of the tool and contains three primary user actions:

1. **New Cohort Configuration** - set the parameters of a cohort from scratch.
2. **Load Cohort Configuration** - load a previously saved JSON or NDJSON file and generate a new set of synthetic data based on those parameters. Optionally edit the pre-existing cohort configuration from the uploaded file.
3. **View Samples** – load previously-created cohort data that can be modified or re-generated.

The site header contains the CohGenT logo, name, and tagline, and "Home" button on the left. Clicking any of these will take you back to the home page from any page.

On the right side of the site header, the dropdown menu has links to "Documentation" (technical documentation and this user guide), the public GitHub repository, and buttons for contacting CohGent developers or reporting a bug or issue. The version number of CohGenT is on the far-right side of the site header.

## New Cohort Configuration

### Set Cohort Scenario and Initial Settings

Select "New Cohort Configuration" to go to the "Cohort Scenario" page. Then choose the cohort scenario you want to use. Cohort scenarios support common public health use cases and align with targeted FHIR Implementation Guides.

> Note: The specific cohort scenario or primary event is driven by the clinical condition the user selects.

Within this step, set the following basic parameters for the new cohort:

- **Cohort Name**
  - **Description:** The name of the cohort being created
  - **Type:** Free text
  - **Required:** Yes
  - **Example**: "Syphilis Patients Aged 16-25"

- **Cohort Timing:**
  - **Primary Clinical Data Period**
    - **Description:** The start and end dates for which the given scenario's primary event of interest (such as a primary condition) must occur.
    - **Type:** Date (MM/DD/YYYY)
    - **Required:** Yes
    - **Example:** Setting the range of 01/01/2025 - 12/31/2025 ensures the primary event only occurs within the year 2025.
  - **Extend Data Until**
    - **Description:** if there is a date for which data should continue beyond the event period end date specified in the previous step.
    - **Type:** Date (MM/DD/YYYY)
    - **Required:** No
    - **Example:** Assuming the primary condition cohort period is January 1, 2025, through December 31, 2025, follow-up labs and procedures can be set to continue beyond that period, such as through June 30, 2026.

## Save Cohort Settings

At any time during cohort creation, if you wish to save the settings you have applied and return later, select "Save Cohort Settings" on the left-hand pane to download the file. Note that generating the completed cohort file is a separate step at the end of the workflow.

## Review, Finalize, and Generate Cohort

### Review Cohort

Review all of the cohort data on the Review Cohort page. To make changes, navigate to previous pages using the left side bar or "Back" button. Select "Next" or move to the "Finalize and Generate" Step once ready.

### Cohort File Generation

The final step in generating a cohort is to confirm the cohort patient count and generate the cohort file. The maximum number of patients in v1.2 is 50.

Here, you can also optionally adjust advanced options, which include:

- **Setting the random seed** – the seed is an arbitrary value used to create reproducible results with randomized data. A random seed is automatically assigned, but an alternate seed can be entered or regenerated. The seed will be automatically saved within the cohort file. If you want to generate different patient data with the same cohort settings, enter or regenerate a different random seed before generating the cohort again.
- **Setting the output file type** – choose between FHIR JSON or FHIR NDJSON file output formats based on your testing needs:

#### FHIR JSON Bundle Format
Selecting **FHIR JSON Bundle** will generate a set of FHIR transaction Bundles organized by patient in the standard JSON format, compressed into a zip file. Each patient's complete medical record (including Patient, Condition, Observations, Procedures, etc.) is contained in a single, self-contained JSON Bundle file.

**Characteristics:**
- Human-readable, hierarchical structure
- Each file contains one complete patient Bundle
- Standard JSON format with proper indentation
- Ideal for individual record review and validation

#### Bulk Data FHIR NDJSON Format
Selecting **Bulk Data NDJSON** will generate a set of Newline Delimited JSON (NDJSON) files following the BULK FHIR format, organized by resource type and compressed into a zip file. Each line in an NDJSON file represents a single, complete FHIR resource as a compact JSON object.

**Characteristics:**
- Streamable, line-oriented format
- Resources grouped by type (e.g., all Patients in one file, all Conditions in another)
- Each line is a valid, compact JSON object (no indentation)
- Optimized for bulk data operations and high-volume processing

#### Format Comparison

| **Aspect** | **FHIR JSON Bundle** | **Bulk Data FHIR NDJSON** |
|---|---|---|
| **Organization** | By patient (one Bundle per patient) | By resource type (all resources of same type together) |
| **File Structure** | Standard JSON with indentation | Newline-delimited, compact JSON |
| **Best For** | Individual patient review, testing single patient workflows, FHIR server transaction uploads | Bulk data import/export, analytics, high-volume testing, streaming data processing |
| **Readability** | High - formatted and hierarchical | Lower - compact, one resource per line |
| **File Size** | Larger (due to formatting) | Smaller (compact format) |
| **Use Cases** | Testing patient-centric workflows, manual review, RESTful API testing | Bulk FHIR API testing, data warehouse loading, large-scale analytics |
| **FHIR Specification** | FHIR Bundle resource | FHIR Bulk Data Access specification |

**When to Use Each Format:**
- Choose **FHIR JSON Bundle** when you need to test individual patient workflows, manually review patient records, or upload data to FHIR servers using transaction Bundles.
- Choose **Bulk Data FHIR NDJSON** when you need to test bulk data operations, perform analytics across many patients, or work with systems that support the FHIR Bulk Data Access API.

Click "Generate FHIR Records", to initiate a cohort generation. Once complete, a new section will appear with the cohort title, generation date, and download button. Click the download button to save the cohort as a zip file. The zip file contains a large set of files of patient bundles in FHIR format.  These bundles are pre-formatted and ready to be uploaded directly to a FHIR server via a RESTful or web client.

# Common Data Entry Types

Many cohort scenarios use the same data entry fields within the tool.
## Distribution Slider

Use the slider to balance the values visually or manually input percentages for precise control. The values will automatically synchronize.

## Distribution Lock

When assigning numeric distributions for more than two categories, use the lock feature to prevent automatic recalculation of distributions.

## Concept Entry

> **Important:** It is highly recommended to identify your relevant code systems and potential codes ahead of time. While CohGenT provides search features and presets, gathering this information in advance makes configuration much smoother and ensures you select the absolute best match for your intended concept.

In the current version of CohGenT, Concepts are entered at the Primary Condition, Clinical Data, and Medications steps. For Primary Condition, there are three different options for entering a concept: Search for Concept, Select Preset Concept, and Enter Concept Manually.

- **Searching for the Concept** involves entering the term (by code or by name) and selecting the correct System (or setting the System dropdown to "All Systems" if the System for that code or name is unknown). The Search results will show all concepts with that code or term, ordered by relevancy. Click on the concept you want, then click "Select" and the System, Code, and Display name will appear and be saved to your cohort.

- **Selecting a Preset Concept** involves opening the Preset Concept List and choosing the concept you want from the list of common conditions. Select "Use this Concept" to save that concept to your cohort. Any previously entered concepts will be over-ridden by new concepts selected.

- **Entering the Concept Manually** involves selecting the system associated with your concept of interest and entering either the code or display name.
    >Note that using this option will not populate codes if left empty.

Searching for the Concept or Entering the Concept Manually are the two mechanisms for entering the Concept for Clinical Data and Medications.

## Date Ranges

To assign onset dates to a clinical event, or to specify an abatement date, adjust the date by X number of days, weeks, months, or years. For clinical events, repetition can also be included by checking the "Repeat" box and inputting X number of days, weeks, months, or years.

# New Cohort Configuration Workflow: Condition-Based Record Cohort Scenario

In the Condition Based Cohort Scenario, CohGenT creates a sequence of clinical events over a defined time period, to simulate disease progression and other data from EHR systems for testing scenarios.

## Summary of Steps: Condition-based Record Scenario

| **Step Name** | **Domain** | **FHIR Resources** | **Required for this Scenario?** | **Singular/Repeating** |
|---|---|---|---|---|
| **Patient Demographics** | Patient | US Core Patient | Yes | Singular Event |
| **Primary Condition** | Problem/Condition | US Core Condition<br>US Core Encounter | Yes | Singular Event |
| **Clinical Data** | Laboratory Results, Procedures, Diagnostic Panels | US Core Laboratory Result<br>US Core Procedure | No | Repeating Events |
| **Medications** | Medication | US Core MedicationStatement | No | Singular Event |

## Complete Example: Syphilis Surveillance Cohort

This example demonstrates creating a cohort for syphilis surveillance with follow-up laboratory testing.

### Example Overview

**Cohort Purpose:** Generate synthetic patient records for testing a syphilis case reporting system with laboratory follow-up data.

**Scenario Details:**
- **Cohort Name:** "Syphilis Patients with Quarterly Lab Follow-up"
- **Patient Count:** 25 patients
- **Primary Condition:** Syphilis (SNOMED CT: 76272004)
- **Time Period:** January 1, 2025 - December 31, 2025
- **Extended Data:** Through June 30, 2026 (for follow-up labs)

### Step-by-Step Configuration

#### 1. Cohort Scenario and Initial Settings

- **Cohort Scenario:** Condition-Based Record
- **Cohort Name:** Syphilis Patients with Quarterly Lab Follow-up
- **Primary Clinical Data Period:** 01/01/2025 - 12/31/2025
- **Extend Data Until:** 06/30/2026

#### 2. Patient Demographics

**Customized Settings:**
- **Age at Diagnosis:** 16-45 years (targeting sexually active population)
- **Sex Distribution:** 
  - Male: 60%
  - Female: 40%
  - Unknown: 0%
- **Geographic Location:** 
  - State: California
  - City: San Francisco
- **Living/Deceased:** 
  - Living: 98%
  - Deceased: 2%
- **Race/Ethnicity:** Using default US census distributions
- **Tribal Affiliation:** Using default 5% prevalence of patients with a tribal affiliation, randomly assign those from the list of federally recognized affiliations.
- **Employment Status:** Using the default (80% employed, 5% unemployed, 15% not in labor force)
- **Occupation:** Randomly assign occupations for those who are employed. 

#### 3. Primary Condition Configuration

**Condition Details:**
- **System:** SNOMED CT
- **Code:** 76272004
- **Display:** Syphilis (disorder)
- **Condition Duration:** Onset Plus 2 weeks to 6 months
  - *Rationale: Simulates varying treatment response times*

#### 4. Clinical Data Sets

**Clinical Data Set 1: Initial Diagnostic Labs**
- **Timing:** At Onset (same day as condition diagnosis), not repeating
- **Lab Panel:** Yes - "Syphilis serology panel"
  - System: LOINC
  - Code: 50690-7
  - Display: Syphilis serology panel

**Lab Tests in Panel:**
1. **RPR (Rapid Plasma Reagin)**
   - System: LOINC
   - Code: 20507-0
   - Display: Reagin Ab [Titer] in Serum by RPR
   - Result Type: Quantity
   - Range: 1:1 to 1:256 (titers)

2. **Treponemal Test (TP-PA)**
   - System: LOINC
   - Code: 5393-9
   - Display: Treponema pallidum Ab [Presence] in Serum
   - Result Type: String
   - Values: "Positive", "Negative", "Indeterminate"

**Clinical Data Set 2: Follow-up Labs**
- **Timing:** Onset Plus 3 months, Repeat every 3 months for 6 months _(to align with extend data until date in the initial settings)_
- **Lab Panel:** No (individual tests)

**Lab Tests:**
1. **RPR Follow-up**
   - System: LOINC
   - Code: 20507-0
   - Display: Reagin Ab [Titer] in Serum by RPR
   - Result Type: Quantity
   - Range: 1:1 to 1:64 (lower titers showing treatment response)

#### 5. Medications

**Medication 1: Benzathine Penicillin G**
- **System:** RxNorm
- **Code:** 105078
- **Display:** Penicillin G benzathine 2.4 MU injection
- **Dosage Instructions:** "2.4 million units IM once weekly for 3 weeks"

**Medication 2: Doxycycline (Alternative for penicillin-allergic patients)**
- **System:** RxNorm
- **Code:** 3640
- **Display:** Doxycycline
- **Dosage Instructions:** "100 mg PO twice daily for 28 days"

Apply Medication 1 to 50% of patients; Apply Medication 2 to 50% of patients

#### 6. Review and Generate

**Generation Settings:**
- **Patient Count:** 25
- **Random Seed:** [Auto-generated or custom]
- **Output Format:** FHIR JSON Bundle (for individual patient review)

### Expected Output

The generated cohort will produce:
- 25 patient bundles (one per patient)
- Each bundle containing:
  - 1 Patient resource
  - 1 Condition resource (Syphilis)
  - 1 Encounter resource (for condition diagnosis)
  - 3-5 Observation resources (initial diagnostic labs)
  - 2-4 sets of follow-up Observation resources (quarterly labs through June 2026)
  - 2 MedicationRequest resources (patients randomly assigned 1 of the 2 based on weighting applied) 
  - Supporting Organization and Practitioner resources

### Use Cases for This Cohort

This synthetic cohort can be used to test:
- Case reporting workflows for syphilis surveillance
- Laboratory result integration and trending
- Medication adherence tracking
- Follow-up care coordination
- FHIR query capabilities for condition-based searches
- Bulk data export for public health reporting

### Patient Demographics

All patient Demographics have preset default settings to mimic US census and OMB distributions. To make changes, select "Customize Patient Demographics". The Demographics Summary will automatically update based on any changes made. Once you are satisfied with patient demographics as shown in the Demographics Summary, select "Next" or navigate to the next step in the left-hand navigation pane.

- **Mask Patient Identifiable Information**
  - **Description:** Option to mask patient identifiable information within the synthetic cohort. If masked, patients will be listed as "masked" in place of synthetic names. Street address and telecom will be omitted entirely. 
  - **Type:** Checkbox
  - **FHIRPath:** Patient.name
  - **Required:** No
  - **Default Behavior:** Names NOT Masked, Street address and telecom present

- **Age At Diagnosis**
  - **Description:** The age of the patient at the time of the primary diagnosis.
  - **Type:** Range
  - **FHIRPath:** Patient.birthDate
  - **Required:** Yes, has defaults
  - **Default Behavior:** 18-65

- **Sex Distribution**
  - **Description:** Distribution of administrative gender within the cohort
  - **Type:** Distribution
  - **FHIRPath:** Patient.gender
  - **Required:** Yes, has defaults
  - **Default Behavior:** Male: 50%, Female: 50%, Unknown: 0%

- **Geographic Location**
  - **Description:** State, City, Line (Street), Zip Code, and Country of the patient's home address
  - **Type:** Location
  - **FHIRPath:** Patient.address
  - **Required:** No
  - **Default Behavior:**
    - State - If none provided, randomized
    - City - If none provided, randomized. _(Note: City can only be entered by user if State is provided. Enter neither, state only, or both city and state)_
    - Line (Street) - Always randomized (No option for user to enter Line (Street))
    - Zip Code - Randomized within the state (No option for user to enter Zip Code)
    - Country - Always US (No option for user to enter Country)

- **Living/Deceased Distribution**
  - **Description:** Distribution of living/dead patients within the cohort
  - **Type:** Distribution
  - **FHIRPath:** Patient.deceased
  - **Required:** Yes, has defaults
  - **Default Behavior:** Living: 100%, Deceased: 0%

- **Race Category Distribution**
  - **Description**: Distribution of US Core Race Categories within the cohort
  - **Type:** Distribution
  - **FHIRPath:** Patient.extension[USCoreRace]
  - **Required:** Yes, has defaults
  - **Default Behavior:** American Indian or Alaskan Native: 2%, Asian: 8%, Black or African American: 15%, Native Hawaiian or Other Pacific Islander: 3%, White: 64%, Other Race: 8%, Unknown: 0%

- **Ethnicity Category Distribution**
  - **Description:** Distribution of US Core Ethnicity Categories within the cohort
  - **Type:** Distribution
  - **FHIRPath:** Patient.extension[USCoreEthnicity]
  - **Required:** Yes, has defaults
  - **Default Behavior:** Hispanic or Latino: 20%, Not Hispanic or Latino, 80%, Unknown: 0%

- **Tribal Affiliation**
  - **Description:** Prevalence of tribal affiliations, such as American Indian, Alaska Native, or Indigenous tribe or nation and whether or not the affiliation should be randomly assigned or specified.
  - **Type:** Distribution
  - **FHIRPath:** Patient.extension
  - **Required:** Yes, has defaults
  - **Default Behavior:** Prevalence of 5% across the cohort of a randomly selected tribal affiliation per patient.

 - **Employment Status**
  - **Description:** Employment Status for the cohort. Unemployed refers to persons who do not currently have employment but are seeking employment. Not in labor force refers to persons who are not employed and not seeking employment.
  - **Type:** Distribution
  - **FHIRPath:** Patient.extension
  - **Required:** Yes, has defaults
  - **Default Behavior:** Employed: 80%, Unemployed: 5%, Not in Labor Force: 15%
  
- **Occupation**
  - **Description:** Occupation for patients in the cohort who are employed. Randomize an occupation per patient or specify a single occupation for the entire cohort.
  - **Type:** Radio button, drop-down
  - **FHIRPath:** Patient.extension
  - **Required:** Yes, has defaults
  - **Default Behavior:** Randomly assign occupation
  
### Primary Condition

Configuration of the primary condition shared by the patients in the cohort. This is the condition being reporting/surveilled.

Use the Concept Finder to search for the condition, use the Quick Condition Selector to select a condition from the provided list of common presets, or enter the condition's concept manually by selecting the appropriate System and entering either the code or display.

Click "Search for Concept" to open the **Concept Finder** and enter in your condition's key word or exact code and system (if known).

Click "Select Quick Condition" to open the **Quick Condition Selector** (with common presets) to select codes for COVID-19, Tuberculosis, RSV, Influenza, or Syphilis.

- **Primary Condition Concept**
  - **Description:** A medical concept that defines the primary event condition. _Note: The Concept's System, Code, and Display make up the Concept._
  - **Type**: Concept
  - **FHIRPath:** Condition.code
  - **Required:** Yes

- **Condition Duration:**
  - **Description:** The expected duration of the primary condition.
  - **Type:** Date Offset
  - **FHIRPath:** Condition.onset, Condition.abatement
  - **Required:** No
  - **Example:** A time frame of "Onset Plus 1 Month to 3 Months" ensures that all conditions will last within 1 to 3 months of the condition's onset.

### Clinical Data 

Add a Clinical Data Set to add Lab Results, Procedures, etc. for each patient in the cohort. Additional clinical data sets can be created for sets with different timing.

For example:
- A set of lab tests being performed weekly is one Clinical Data Set
- A procedure performed every 6 months is a second Clinical Data Set

#### Add Clinical Data Set

Add a Clinical Data Set to add one or more of Lab Results, Procedures, or Radiology Reports. for each patient in the cohort. Additional clinical data sets can be created for sets with different timing.
For example:
•	A set of lab tests being performed weekly as one Clinical Data Set
•	A procedure performed every 6 months as a second Clinical Data Set


**Clinical Data Set Settings**

- **Timing**
  - **Description:** The time frame in which this event sets takes place with relation to the primary condition event.
  - **Type**: Date Offset with Repetition
  - **FHIRPath:** Observation.date, Procedure.date
  - **Required:** No
  - **Example:** A time frame of "Onset Plus 1 Week Repeat every 3 Months" will ensure the information within this event occurs 1 week after the primary condition event, then 3 months after until the Cohort End date or when the end date is specified.

- **Create Clinical Data Set as a Lab Panel?**
  - **Description:** Select this to create this clinical data set as a lab panel. All members of the clinical data set should be members of the specified panel. If selected, provide a concept for the panel.
  - **Type:** Checkbox
  - **Required**: No

#### Add Lab/Observation 

Assign a lab result to the current event set.

- **Lab/Observation Result Code**
  - **Description:** A medical concept that defines the laboratory observation.
  - **Type:** Concept
  - **FHIRPath:** Observation.code
  - **Required:** No

- **Result: Quantity**
  - **Description:** The range of values for the lab result. Individual patients' lab results will span randomly across the set range.
  - **Type:** Range
  - **FHIRPath:** Observation.valueQuantity
  - **Required:** No

- **Result: String**
  - **Description:** The character value for the lab result. Add multiple values to have patients' lab results randomly assigned to the different values you entered.
  -  **Type:** String
  - **FHIRPath:** Observation.valueString
  - **Example:** Low, Medium, and High value strings
  - **Required:** No

#### Add Procedure

- **Procedure Result Code**
  - **Description:** A medical concept that defines the procedure performed.
  - **Type:** Concept
  - **FHIRPath:** Procedure.code
  - **Required:** No


#### Add Radiology Report

- **Radiology Report Result Code**
  - **Description:** A medical concept that defines the radiology procedure.
  - **Type:** Concept
  - **FHIRPath:** DiagnosticReport.code
  - **Required:** No

### Medications

Add a Medication Set to specify medications. Add more than one set and assign weighted values to specify which proportion of the cohort receives which medications.


- **Medication**
  - **Description**: A medical concept that defines the medication. _Note: The Concept's System, Code, and Display make up the Concept._
  - **Type:** Concept
  - **FHIRPath:** MedicationRequest.code
  - **Required:** No

- **Dosage Instructions**
  - **Description:** Details on how medication should be taken.
  - **Type:** Text
  - **FHIRPath:** MedicationRequest.dosageInstruction
  - **Required:** No

# Advanced Examples

## Example: Combining Multiple Cohorts for Mixed Population Testing

This advanced example demonstrates creating two separate cohorts with different characteristics and combining them to simulate a more realistic, heterogeneous patient population for testing.

### Why Combine Cohorts?

Real-world public health scenarios often involve diverse patient populations with varying disease stages, demographics, and clinical presentations. Combining cohorts allows you to:
- Test systems with different population diversity
- Simulate different disease stages or severity levels
- Create control groups alongside case groups
- Test data analytics and reporting across subpopulations
- Validate query capabilities across distinct patient characteristics

### Combined Cohort: Tuberculosis Surveillance - Early vs. Late Stage

In this example, we will generate a mixed population of TB patients at different disease stages to test case classification, treatment protocols, and outcome tracking.

**Cohort A: Early-Stage TB (Latent/Newly Diagnosed)**
- Recently diagnosed, minimal symptoms
- Basic diagnostic labs
- Standard first-line treatment

**Cohort B: Late-Stage TB with Complications**
- Advanced disease with complications
- Extensive diagnostic workup
- Complex treatment regimens including second-line drugs

### Cohort A Configuration: Early-Stage TB

#### Basic Settings
- **Cohort Name:** "TB Early Stage - Latent and Newly Diagnosed"
- **Primary Clinical Data Period:** 01/01/2025 - 12/31/2025
- **Extend Data Until:** 06/30/2026

#### Demographics

- **Age at Diagnosis:** 25-55 years (working-age population)
- **Sex Distribution:** Male: 55%, Female: 45%
- **Geographic Location:** 
  - State: New York
  - City: New York City
- **Living/Deceased:** Living: 100%, Deceased: 0%
- **Race, Ethnicity and Tribal Affiliation**: Default
#### Primary Condition
- **System:** SNOMED CT
- **Code:** 56717001
- **Display:** Tuberculosis (disorder)
- **Condition Duration:** Onset Plus 6 months to 12 months

#### Clinical Data Sets

**Clinical Data Set 1: Initial Diagnostic Workup**
- **Timing:** At Onset

**Lab Tests:**
1. **Mycobacterium Tuberculosis Stimulated Gamma Interferon Panel (TST)**
   - System: LOINC
   - Code: 71775-1
   - Display: Mycobacterium tuberculosis stimulated gamma interferon panel - Blood
   - Result Type: String
   - Values: "Positive": 99.5%, "Negative": 0.05%

2. **Chest X-Ray Chest Views**
   - System: LOINC
   - Code: 30745-4
   - Display: XR Chest Views
   - Result Type: String
   - Values: "Normal": 0.1%, "Minimal infiltrates": 2%, "Small nodules:97.9%"

**Clinical Data Set 2: Follow-up Monitoring**
- **Timing:** Onset Plus 1 month, Repeat every 2 months

**Lab Tests:**
1. **Sputum Culture**
   - System: LOINC
   - Code: 543-9
   - Display: Mycobacterium tuberculosis [Presence] in Sputum by Organism specific culture
   - Result Type: String
   - Values: "Negative": 2%, "Positive - low count": 98%

#### Medications
**Medication 1: Isoniazid**
- System: RxNorm
- Code: 6038
- Display: Isoniazid
- Dosage: "300 mg PO daily for 9 months"

**Medication 2: Rifampin**
- System: RxNorm
- Code: 9384
- Display: Rifampin
- Dosage: "600 mg PO daily for 9 months"

### Cohort B Configuration: Late-Stage TB with Complications

#### Basic Settings
- **Cohort Name:** "TB Late Stage - Advanced Disease with Complications"
- **Primary Clinical Data Period:** 01/01/2025 - 12/31/2025
- **Extend Data Until:** 12/31/2026 (longer follow-up for complex cases)

#### Demographics

**Customized Settings:**
- **Age at Diagnosis:** 45-75 years (older population with comorbidities)
- **Sex Distribution:** Male: 65%, Female: 35%
- **Geographic Location:** 
  - State: New York
  - City: New York City (same location for comparison)
- **Living/Deceased:** Living: 85%, Deceased: 15% (higher mortality)
- **Race, Ethnicity and Tribal Affiliation**: Default

#### Primary Condition
- **System:** SNOMED CT
- **Code:** 154283005
- **Display:** Pulmonary tuberculosis (disorder)
- **Condition Duration:** Onset Plus 12 months to 24 months (longer treatment)

#### Clinical Data Sets

**Clinical Data Set 1: Extensive Initial Workup**
- **Timing:** At Onset

**Lab Tests:**
1. **Portable XR Chest Views**
   - System: LOINC
   - Code: 30746-2
   - Display: Portable XR Chest Views
   - Result Type: String
   - Values: "Normal": 0.1%, "Minimal infiltrates": 2%, "Small nodules:97.9%"

2. **Sputum AFB Smear**
   - System: LOINC
   - Code: 14556-7
   - Display: Acid fast bacillus [Presence] in Sputum by Light microscopy
   - Result Type: String
   - Values: "3+ Positive", "4+ Positive"

3. **Drug Susceptibility Testing**
   - System: LOINC
   - Code: 559-5
   - Display: Mycobacterium tuberculosis rifampin resistance
   - Result Type: String
   - Values: "Susceptible", "Resistant"

**Clinical Data Set 2: Intensive Monitoring**
- **Timing:** Onset Plus 2 weeks, Repeat every 2 weeks

**Lab Tests:**
1. **Sputum Culture with Quantification**
   - System: LOINC
   - Code: 85581-7
   - Display: Mycobacterium avium and Mycobacterium intracellulare DNA [Identifier] in Sputum or Bronchial by NAA with probe detection
   - Result Type: String
   - Values: "Positive - high count": 48%, "Positive - moderate count": 40%, "Positive - low count": 10%, "Negative": 2%

2. **Liver Function Tests** (monitoring for drug toxicity)
   - System: LOINC
   - Code: 1742-6
   - Display: Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma
   - Result Type: Quantity
   - Range: 7-52 U/L 9Normal Range)

#### Medications

**Medication 1: Isoniazid (First-line)**
- System: RxNorm
- Code: 6038
- Display: Isoniazid
- Dosage: "300 mg PO daily"

**Medication 2: Rifampin (First-line)**
- System: RxNorm
- Code: 9384
- Display: Rifampin
- Dosage: "600 mg PO daily"

**Medication 3: Pyrazinamide (First-line)**
- System: RxNorm
- Code: 8987
- Display: Pyrazinamide
- Dosage: "1500 mg PO daily"

**Medication 4: Ethambutol (First-line)**
- System: RxNorm
- Code: 4119
- Display: Ethambutol
- Dosage: "1200 mg PO daily"

**Medication 5: Levofloxacin (Second-line for resistant cases)**
- System: RxNorm
- Code: 82122
- Display: Levofloxacin
- Dosage: "750 mg PO daily"

### Combining the Cohorts

#### Method 1: Generate Separately and Merge Files

1. **Generate Cohort A:**
   - Configure and generate "TB Early Stage" cohort
   - Download as FHIR JSON Bundle format
   - Save to a designated folder (e.g., `TB_Early_Stage/`)

2. **Generate Cohort B:**
   - Configure and generate "TB Late Stage" cohort  
   - Download as FHIR JSON Bundle format
   - Save to a different folder (e.g., `TB_Late_Stage/`)

3. **Merge the Cohorts:**
   - Extract both ZIP files
   - Combine all patient bundle files into a single directory
   - Result: 50 total patient bundles (30 early-stage + 20 late-stage)

#### Method 2: Using Bulk FHIR NDJSON Format

1. **Generate Both Cohorts as NDJSON:**
   - Generate Cohort A with Bulk Data NDJSON format
   - Generate Cohort B with Bulk Data NDJSON format

2. **Merge NDJSON Files by Resource Type:**
   - Combine Patient.ndjson files (append Cohort B patients to Cohort A)
   - Combine Condition.ndjson files
   - Combine Observation.ndjson files
   - Combine MedicationRequest.ndjson files
   - Combine all other resource type files

3. **Result:** Single set of NDJSON files containing all 50 patients organized by resource type

### Key Differences Between Cohorts

| **Characteristic** | **Cohort A (Early-Stage)** | **Cohort B (Late-Stage)** |
|---|---|---|
| **Patient Count** | 30 | 20 |
| **Age Range** | 25-55 years | 45-75 years |
| **Mortality Rate** | 0% | 15% |
| **Condition Duration** | 6-12 months | 12-24 months |
| **Initial Diagnostic Tests** | 2 tests | 3 tests |
| **Follow-up Frequency** | Every 2 months | Every 2 weeks |
| **Medication Count** | 2 (first-line only) | 5 (first + second-line) |
| **Extended Data Period** | 6 months | 12 months |
| **Disease Severity** | Latent/Minimal | Advanced/Complicated |

### Use Cases for Combined Cohorts

This combined TB cohort dataset can be used to test:

1. **Population Health Analytics:**
   - Compare outcomes between early and late-stage diagnosis
   - Analyze treatment effectiveness across disease stages
   - Calculate mortality rates by subpopulation

2. **Clinical Decision Support:**
   - Test algorithms that recommend different treatment protocols based on disease stage
   - Validate drug interaction checking across simple and complex regimens

3. **Public Health Reporting:**
   - Test case classification systems (latent vs. active TB)
   - Validate reporting workflows for different disease stages
   - Test contact tracing prioritization (higher priority for late-stage cases)

4. **FHIR Query Capabilities:**
   - Query for patients by disease severity
   - Filter by medication regimen complexity
   - Search across different diagnostic test results

5. **Data Visualization and Dashboards:**
   - Create stratified views by disease stage
   - Display treatment adherence across subpopulations
   - Show outcome trends for different patient groups

### Technical Considerations

**Patient ID Uniqueness:**
- Each cohort generation creates unique patient IDs
- No risk of ID collision when combining cohorts
- Each patient maintains referential integrity within their bundle

**Random Seed Management:**
- Use different random seeds for each cohort to ensure variation
- Document seeds used for reproducibility
- Consider using seeds that indicate cohort type (e.g., 1000 for Cohort A, 2000 for Cohort B)

**Temporal Alignment:**
- Both cohorts use the same primary clinical data period (2025)
- Different extended data periods reflect different follow-up needs
- Ensure date ranges make sense when analyzing combined data

**Resource References:**
- Organization and Practitioner resources are auto-generated per cohort
- May result in duplicate organizations when combining
- This is acceptable for testing purposes and reflects real-world scenarios

### Tips for Creating Combined Cohorts

1. **Plan Demographics Carefully:** Ensure demographic differences reflect realistic population characteristics
2. **Use Consistent Geography:** Keep location consistent (or intentionally vary) based on testing needs
3. **Vary Clinical Complexity:** Create clear distinctions in clinical data complexity between cohorts
4. **Document Differences:** Maintain clear documentation of what distinguishes each cohort
5. **Test Incrementally:** Generate and validate each cohort individually before combining
6. **Consider File Format:** Choose NDJSON for easier programmatic merging, JSON Bundles for manual review

# FAQs

## General Questions

**What is CohGenT and who is it for?**

CohGenT (Cohort Generation Tool) is a software application designed to help FHIR developers, public health maintainers, and data analysts create and manage synthetic cohort data. It reduces the barrier-to-entry for testing applications with FHIR by providing common scenarios and a simple-to-use interface for creating synthetic patient data.

**What is synthetic data and why would I use it?**

Synthetic data is artificially generated patient data that mimics real patient characteristics without containing any actual patient information. This allows you to test interoperability workflows and data exchange scenarios without privacy concerns or the need for real patient data.

**What can CohGenT help me do?**

CohGenT helps you create synthetic patient cohorts for testing public health scenarios, generate FHIR JSON bundles ready for upload to test services, and create shareable cohort files that can be reused by others.

## Getting Started

**What is a "Cohort Scenario"?**

A Cohort Scenario is a pre-designed template that describes your cohort. These scenarios are developed based on common public health use cases and adhere to targeted FHIR Implementation Guides. When you start a new cohort, you first select a Cohort Scenario that matches your testing needs.

**Do I need to understand FHIR technical specifications to use CohGenT?**

While a basic understanding of FHIR is helpful, CohGenT provides a user-friendly interface that simplifies the process of creating FHIR-compliant data. The tool is designed to reduce technical barriers.

## Cohort Configuration

**What patient demographics can I customize?**

You can configure several demographic characteristics including age at diagnosis, sex distribution, geographic location (state and city), living/deceased distribution, race category distribution, and ethnicity category distribution. All settings have defaults, so you only need to change them if your scenario requires specific demographics.

**Can I protect patient privacy in the generated data?**

All data generated is synthetic and does not represent real patients.

**What is a "Condition Code" and why is it required?**

A Condition Code is a medical concept that defines the primary health condition shared by patients in your cohort. This is typically the condition being reported or surveilled in your public health scenario. It's required because it forms the basis of your cohort definition.

## Clinical Data Configuration

**Can I add medications to my synthetic patients?**

Yes. You can configure a list of medications to include for each patient in the cohort by specifying the Medication Code (the medical concept defining the medication) and optional dosage instructions.

**What are "Additional Clinical Events/Entities"?**

These allow you to define one or more event sets of periodic lab results and/or procedures over the cohort time period. For example, you can add lab results by specifying a Result Code, and the result value (either as a quantity range or string).

**What does "Abatement Date Range" mean?**

The Abatement Date Range defines when a condition resolves or ends, relative to when it started (the onset). For example, setting "Onset Plus 1 Month to 3 Months" ensures all conditions in your cohort will resolve within 1 to 3 months after they begin.

## Data Quality and Validation

**How do I know my generated data meets FHIR standards?**

CohGenT generates data that adheres to configurable FHIR profiles, including US Core. The exports can be validated to ensure they meet required FHIR specifications.

**What format does CohGenT export data in?**

CohGenT generates FHIR JSON bundles that are ready for upload to test services.

## Sharing and Reuse

**Can I share my cohort design with colleagues?**

Yes. CohGenT creates cohort files that users can share for reuse, making it easy to collaborate or replicate testing scenarios across teams.

# Contact Information

For additional information, feedback, or questions about CohGenT, please contact Plamen.Tassev@gtri.gatech.edu.

> **Note:** This contact information will need to be updated in May.

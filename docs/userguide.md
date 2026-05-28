# CohGenT User Guide (DRAFT)

<mark>new/edited content for CDC's review is highlighted</mark>

# Introduction

CohGenT (the Cohort Generation Tool), is a software application <mark>designed for data analysts and FHIR developers in the realm of public health and epidemiology</mark> to assist in creating and managing synthetic cohort data. Within CohGenT, "cohorts" are defined groups of synthetic patients following specific exposures or characteristics that influence the development of health outcomes. CohGent reduces the barrier-to-entry to testing applications with FHIR, providing common scenarios and a simple-to-use interface for those who need to create synthetic patient data.

CohGenT generates synthetic data for testing data exchange including testing interoperability workflows. Generated data adheres to configurable FHIR profiles, including US Core, and exports can be validated to ensure they meet required FHIR specifications.
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
- Medications <mark>(1.1)</mark>

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
    - **Example:** Setting a date of 06/31/2026 will follow the patient resources with periodic follow up labs and procedures until 06/31/2026.

## Save Cohort Settings

At any time during cohort creation, if you wish to save the settings you have applied and return later, select "Save Cohort Settings" on the left-hand pane to download the file. Note that generating the completed cohort file is a separate step at the end of the workflow.

## Review, Finalize, and Generate Cohort

### Review Cohort

Review all of the cohort data on the Review Cohort page. If edits need to be made, navigate to previous pages using the left side bar or "Back" button. Select "Next" or move to the "Finalize and Generate" Step once ready.

### Cohort File Generation

The final step in generating a cohort is to confirm the cohort patient count and generate the cohort file. The maximum number of patients in v1.0 is 50.

Here, you can also optionally adjust advanced options, which include:

- **Setting the random seed** – the seed is an arbitrary value used to create reproducible results with randomized data. A random seed is automatically assigned, but an alternate seed can be entered or regenerated. The seed will be automatically saved within the cohort file. If you want to generate different patient data with the same cohort settings, enter or regenerate a different random seed before generating the cohort again.
- **Setting the output file type** – <mark>more info and instructions are being added here</mark>  choose between a JSON or NDJSON file output. Selecting FHIR JSON Bundle will generate a set of FHIR transaction Bundles by patient in the JSON format, compressed into a zip file. Selecting Bulk Data NDJSON will generate a set of New-line Delimited JSON files in the BULK FHIR format, divided by resource type, compressed into a zip file. 

Click "Generate Cohort", to trigger an automatic download of a zip file. These bundles are pre-formatted and ready to be uploaded directly to a FHIR server via a RESTful or web client.

# Common Data Entry Types

Many cohort scenarios use the same data entry fields within the tool.
## Distribution Slider

Use the slider to balance the values visually or manually input percentages for precise control. The values will automatically synchronize.

## Distribution Lock

When assigning numeric distributions for more than two categories, use the lock feature to prevent automatic recalculation of distributions.

## Concept Entry

In the current version of CohGenT, Concepts are entered at the Primary Condition, Clinical Data, and Medications steps. For Primary Condition, there are three different options for entering a concept: Search for Concept, Select Preset Concept, and Enter Concept Manually.

Searching for the Concept involves entering the term (by code or by name) and selecting the correct System (or setting the System dropdown to "All Systems" if the System for that code or name is unknown). The Search results will show all concepts with that code or term, ordered by relevancy. Click on the concept you want, then click "Select" and the System, Code, and Display name will appear and be saved to your cohort.

Selecting a Preset Concept involves opening the Preset Concept List and choosing the concept you want from the list of common conditions. Select "Use this Concept" to save that concept to your cohort. Any previously entered concepts will be over-ridden by new concepts selected.

Entering the Concept Manually involves selecting the system associated with your concept of interest and entering either the code or display name.

Searching for the Concept or Entering the Concept Manually are the two mechanisms for entering the Concept for Clinical Data and Medications.

## Date Ranges

To assign onset dates to a clinical event, or to specify an abatement date, adjust the date by X number of days, weeks, months, or years. For clinical events, repetition can also be included by checking the "Repeat" box and inputting X number of days, weeks, months, or years.

# New Cohort Configuration Workflow: Condition-Based Record Cohort Scenario

In the Condition Based Cohort Scenario, CohGenT creates a sequence of clinical events over a defined time period, to simulate disease progression and other data from EHR systems for testing scenarios.

## Summary of Steps: Condition-based Record Scenario

| **Step Name** | **Domain** | **FHIR Resources** | **Required for this Scenario?** | **Singular/Repeating** |
|---|---|---|---|---|
| **Patient Demographics** | Patient | US Core Patient | Yes | Singular Event |
| **Condition** | Problem/Condition | US Core Condition<br>US Core Encounter | Yes | Singular Event |
| **Clinical Data** | Laboratory Results, Procedures, Diagnostic Panels | US Core Laboratory Result<br>US Core Procedure | No | Repeating Events |
| **Medications** | Medication | US Core MedicationStatement | No | Singular Event |

### Patient Demographics

All patient Demographics have preset default settings to mimic US census and OMB distributions. To make changes, select "Customize Patient Demographics". The Demographics Summary will automatically update based on any changes made. Once you are satisfied with patient demographics as shown in the Demographics Summary, select "Next" or navigate to the next step in the left-hand navigation pane.

- **Mask Patient Names**
  - **Description:** Option to mask patient names within the synthetic cohort. If masked, patients will be listed as "masked" in place of synthetic names.
  - **Type:** Checkbox
  - **FHIRPath:** Patient.name
  - **Required:** No
  - **Default Behavior:** Names NOT Masked

- **Age At Diagnosis**
  - **Description:** The age of the patient at the time of the primary diagnosis.
  - **Type:** Range
  - **FHIRPath:** Patient.Name
  - **Required:** Yes, has defaults
  - **Default Behavior:** 18-65

- **Sex Distribution**
  - **Description:** Distribution of gender within the cohort
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

### Primary Condition

Configuration of the primary condition shared by the patients in the cohort. This is the condition being reporting/surveilled.

Use the Concept Finder to search for the condition, use the Quick Condition Selector to select a condition from the provided list of common presets, or enter the condition's concept manually by selecting the appropriate System and entering either the code or display.

Click "Search for Concept" to open the **Concept Finder** and enter in your condition's key word or exact code and system (if known).

Click "Select Quick Condition" to open the **Quick Condition Selector** (with common presets) to select codes for COVID-19, Tuberculosis, RSV, Influenza, and Syphilis.

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

Assign Clinical Data Set Settings to establish the timing of the data relative to the primary condition onset, then add one or multiple types of clinical data for that time period.

**Clinical Data Set Settings**

- **Timing**
  - **Description:** The time frame in which this event sets takes place with relation to the primary condition event.
  - **Type**: Date Offset with Repetition
  - **FHIRPath:** Observation.date, Procedure.date
  - **Required:** No
  - **Example:** A time frame of "Onset Plus 1 Week Repeat every 3 Months" will ensure the information within this event occurs 1 week after the primary condition event, then 3 months after until the Cohort End date.

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
  - **Type:** String
  - **FHIRPath:** Observation.valueString
  - **Example:** Low, Medium, and High value strings
  - **Required:** No

#### Add Radiology Report

- **Lab/Observation Result Code**
  - **Description:** A medical concept that defines the laboratory observation
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
  - **Type:** String
  - **FHIRPath:** Observation.valueString
  - **Example:** Low, Medium, and High value strings
  - **Required:** No

### Medications

Configure the list of medications for the cohort of patients.
<mark> note: this is going to change slightly in the next release</mark> 
Use the Concept Finder to search for the medication or enter the Concept manually by selecting the appropriate System and entering either the code or display.

- **Medication**
  - **Description**: A medical concept that defines the medication. _Note: The Concept's System, Code, and Display make up the Concept._
  - **Type:** Concept
  - **FHIRPath:** MedicationStatement.code
  - **Required:** No

- **Dosage Instructions**
  - **Description:** Details on how medication should be taken.
  - **Type:** Text
  - **FHIRPath:** MedicationStatement.dosage
  - **Required:** No

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

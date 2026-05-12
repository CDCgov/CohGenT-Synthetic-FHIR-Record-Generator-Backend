# CohGenT (Cohort Generator Tool) API/Backend Service

*Note: This README's core information is focused on the CohGenT API backend service, while the deployment section provides information on the broader stack.*

## Core CohGenT API Features

- Provide an interface for generating Patient Health Records as FHIR Resources using the FHIR Sheets library.
- Provide common preset values for measurements to shape generation (e.g., low, normal, and high ranges for common lab tests).
- Allow searching against an OMOP Common Data Model database's Concept table.

## Description

The CohGenT (Cohort Generator Tool) API is the backend data generation component for the broader CohGenT application stack. CohGenT uses simplified user input to generate FHIR records based on a designed "use case" or "scenario". A scenario is a set of entity definitions aligned to FHIR Resources (but which are not FHIR Resources themselves) which dictate how data is generated to "fill in the blank" for the FHIR Sheets library (a Python library which parses tabular data into FHIR Resource objects). The CohGenT API does not produce FHIR Resources itself, it only creates the data fed into FHIR Sheets.

Data is generated as a "cohort" of synthetic patients. The data that is generated is directed by a set of user provided cohort settings and the specified "scenario" entity models.

While the CohGenT API can be used directly with proper understanding of the input models, it is intended to be used in conjunction with the CohGenT UI frontend. It also provides resources for the sake of the frontend application such as healthcare terminology searching against an OMOP CDM Database.

The CohGenT API is written in Python using the FastAPI Framework, with significant use of Pydantic and SQLAlchemy. (Note that while this backend is labeled "API" as it is abstractly an interface between the UI, the FHIR Sheets library, and databases, it does contain core generation services as well, so the label is partially a misnomer.)

For more information, please see the official CohGenT Document at #TODO ADD LINK

## OMOP Common Data Model Overview

The Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM) is a healthcare research database schema maintained by the Observational Health Data Sciences and Informatics (OHDSI) program. It includes tables to support standardized healthcare terminology, covering systems such ICD-10, LOINC, and SNOMED. Each code within a system represents a "concept", and multiple systems can reference the same real world concept. (For example, there are diagnostic codes for Type 2 Diabetes in both ICD-10 and SNOMED.) The OMOP CDM provides a middle ground built to support all concepts in consistent model, and ways to draw relationships betwee ncodes both within and across terminology systems.

In CohGenT, the OMOP CDM Concept tables are used to support users in searching for standardized concepts (e.g. lab or diagnostic codes), while ensuring the tables are maintainable. This is achieved by using the OHDSI Athena tool, which provides downloads of major terminology systems as CSVs for the OMOP CDM.

For more information, please see:
- [Main OHDSI Website](https://www.ohdsi.org/)
- [OMOP CDM 5.4 Documentation](https://ohdsi.github.io/CommonDataModel/cdm54.html)
- [Athena](https://athena.ohdsi.org/)

## Configuration Options
Configuration uses the Pydantic Settings module. (https://docs.pydantic.dev/latest/concepts/pydantic_settings/) For complete information, please review their documentation. For this application, an example approach to configuration is provided as dotenv file, `example.env` which is reproduced below.

```
APP_TAG="example"
VERSION_TAG="example"
LOG_LEVEL= "INFO"
DATABASE_URL="sqlite:///./app.db"
OMOP_DATABASE_URL="sqlite:///./omop.db"
SHOW_FHIRSHEETS_LOGS=False
ENABLE_RUN_LOGS=False
ITERATION_LIMIT=100
ROOT_PATH="/api"
FORCE_RESEED=False
CORS_ORIGINS="*"
```
*Note: Database connection string placeholders use SQLite to have a functional default, though use of SQLite is not recommended.*

The settings are as follows:
* App Tag - This allows users to add tags following the application name when retrieved from the `/info` endpoint. This allows for such things as easy distinction of different environments. For example, setting this field to `"dev"` would cause the application to be labeled as "CohGenT - Cohort Generation Tool API dev".
* Version Tag - This is the same as App Tag but for version, appending the tags to the internal version number (specified at the top of `main.py`). It is intended for developers/maintainers though may be used for general deployments as appropriate.
* Log Level - The log level to capture.
* Database URL - This is the main database and is required for many application features to function. Setting this URL will cause the database itself to be built on startup. Please see the deployment section for more information.
* OMOP Database URL - This is the optional OMOP CDM database for terminology searching. Please see the deployment section for more information.
* Show FHIRSheets Logs - Whether or not to enable logging FHIR Sheets output. FHIR Sheets can be verbose in its warning output due to the way generation functions, and it is recommended to keep this disabled.
* Enable Run Logs - Whether or not to provide a thorough run specific log for each generation. These files document the user settings provided to the API, information about the scenario being built against, and the FHIR Sheets models. **WARNING** These files are large! While this can be used for troubleshooting or strict record keeping, it is *not* recommended to enable this for production deployments with many users.
* Iteration Limit - The maximum number of repeating "event set" loops. This is provided a fail safe for users creating potentially untenable levels of data generation (e.g., a set of CMP and CBC labs generated daily over the course of years). This is a non-biased limit that will break out of the generation when the count is reached.
* Force Reseed - Forces a reload of the lab value preset seed file (see the section of the document on Lab Value Presets, the seed CSV, and the database tables later in this document). **WARNING: Setting this to True can be a destructive action as it will clear the entire related table. Any custom presets added through the API Will be lost.**
* CORS Origins - Sets the allowed origins in CORS settings from a comma separated list. Default is *, which means all allowed origins. For more secured environments, this should be set to a list of available origins. `"https://cohgent.example.com, https://cohgent.com"`. For more information on CORS origins, please see the FastAPI Documentation at [https://fastapi.tiangolo.com/tutorial/cors/](https://fastapi.tiangolo.com/tutorial/cors/).

**Note:** For Postgres databases, please use the prefix `postgresql+psycopg://` to ensure that the correct driver is utilized.

In addition to the `example.env` file, a `local.env` is provided for the Docker Compose deployment (see the Deployment section of this README below).

## Architecture

![CohGenT Architecture](./docs/architecture.png)

### Components

* CohGenT UI (Angular - Typescript)
  * Frontend user facing application.
* CohGenT API (Fast API - Python)
  * Backend API to serve the UI, provides data element level generation which is provided to FHIR Sheets to build FHIR Resources.
* FHIR Sheets
  * Library/CLI Tool that takes in tabular data to generate FHIR Resources.
* CohGenT Database
  * Database that supports internal CohGenT requirements to function.
* OMOP CDM Database
  * Database in the OMOP CDM schema populated with concepts from the Athena tool. Supports terminology searching.
    * Expected terminology systems:
      * ICD10CM    International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS)
      * ICD10PCS    ICD-10 Procedure Coding System (CMS)
      * ICD10    International Classification of Diseases, Tenth Revision (WHO)
      * Race    Race and Ethnicity Code Set (USBC)
      * Gender    OMOP Gender
      * NDC    National Drug Code (FDA and manufacturers)
      * RxNorm    RxNorm (NLM)
      * LOINC    Logical Observation Identifiers Names and Codes (Regenstrief Institute)
      * CPT4    Current Procedural Terminology version 4 (AMA)
      * SNOMED    Systematic Nomenclature of Medicine - Clinical Terms (IHTSDO)

## Deployment

### System Requirements/Recommendations

The CohGenT Core Application Stack is lightweight and should run on any modern systems, so specific CPU and RAM requirements are not provided.

**Database Requirements:**
- Main Application Database
  - Recommended Database: Postgres
  - Disk Space: 2 GB minimum.
- OMOP CDM Database
  - Recommended Database: Postgres
  - Disk Space: 5 GB minimum. 
  - (Note: 2 GB for current required terminology systems, plus future expansion and working space.)

**Other Requirements:**
- UMLS Terminology Service Account w/ API Key - [https://uts.nlm.nih.gov/uts/](https://uts.nlm.nih.gov/uts/)
  - (Note: Used for loading CPT4 terminology system for the OMOP CDM database.)

**Deployment Requirements:**
- For Docker Compose Deployment, Docker or Equivalent (Docker Desktop/Podman/etc.)
- For non-Docker Deployment of the Backend Service, Python Web Server (Uvicorn/Hypercorn/etc.)
- For non-Docker Deployment of the Frontend UI, generic static asset web server (NGINX/etc.)
  - (Note: For non-Docker deployment requirements, they are discussed further in the relevant deployment steps.)

Note: For non-Docker deployments, architecture is not assumed. Specific examples provided in the deployment steps

### Deploy using Docker Compose

For a simple, local deployment, the CohGenT software stack can be deployed using the provided Docker Compose file (`compose.yaml`) found in the CohGenT-API repository.

The Compose file includes 4 services: `cohgent-ui` (frontend), `cohgent-api` (backend), `cohgent-db`, and `omop-db`. `omop-db` is commented out by default, and is provided only to demonstrate setting up a secondary database dedicated to the OMOP CDM model for the terminology search feature. The databases may be served from the same container (running a single database server) if desired, or managed separately due to the complexity of managing the OMOP CDM vocabulary tables. *Using the Compose deployment, the OMOP CDM scheme is not setup and the vocabularly is not loaded due to this complexity, only the container infrastructure is deployed for it. For more information, see the section of this README on loading the OMOP CDM Database.* The application will run without the OMOP CDM database, allowing for demoing/testing, but the terminology search features will not work until the OMOP database is fully configured. The recommended approach is to use the compose file to build the containers however you would like your final database structure to be (same or separate postgres servers), to be able to manage the stack as a whole later. Then, with the infrastructure is stood up, you may populate the OMOP CDM tables once the compose stack is running and core integration tested. This will avoid long build times in case there is an error that needs to be troubleshooted.

Follow the step by step instructions below to deploy using Docker Compose. Note that instructions for loading the OMOP CDM tables are given separately as they apply to all approaches to deployment.

#### Step 1 - Download Complete Stack

As the frontend code is kept separately, this approach assumes that the frontend code is cloned or downloaded into a `/ui/` subfolder of this API repository folder, using it as the project root folder, as follows:
```
[project root]/
├── README.md <--- The file you are reading.
├── compose.yaml
├── Dockerfile.local
├── local.env
├── local.ui-config.json
├── api/
│   ├── main.py
│   └── (etc.)
└── ui/ <--- UI CODE SHOULD BE HERE!
```

#### Step 2 - Configure Optional Settings and Ports

The Docker Compose deployment for CohGenT includes two files that can be set on the host machine: `local.env` for the backend service and `local.ui-config.json` for the frontend user interface. These use volume mounting to bind these files directly into the docker containers at the location where the configuration would reside inside the container. For the CohGenT API backend service, the compose file binds the `local.env` to the internal container `.env` file. This is also the case for the `local.ui-config.json` file, which manages the UI settings by binding to the internal UI container `config.json`.

While most settings should not need to be changed for a local compose deployment, you may have to modify certain database related settings. In the `local.env` file you will see the following two lines:
```
DATABASE_URL="postgresql+psycopg://cohgent:testpassword@cohgent-db:5432/cohgent"
OMOP_DATABASE_URL="postgresql+psycopg://cohgent:testpassword@omop-db:5432/omop"
```

These are the database connection strings used by the API to connect to the databases, using the Docker bridge network defined in the Compose file. (For more information on Docker networking, please see [https://docs.docker.com/engine/network/](https://docs.docker.com/engine/network/).) The default settings, including the username and password, match what is configured in the Compose file for the two database services. Note that `OMOP_DATABASE_URL` points to the service which is commented out by default. If you uncomment out that service and load the terminology to the database specified (the `/omop` part of the string), this should work as is shown in the default `local.env` settings. Otherwise, you should update the `OMOP_DATABASE_URL` as appropriate. For example, if you were to decide to load the OMOP CDM tables and content in the same database container as the main `cohgent-db`, using a database called `omop`, you would set the string what's below, swapping out the name of the Compose defined service from `omop-db` to `cohgent-db`.
```
OMOP_DATABASE_URL="postgresql+psycopg://cohgent:testpassword@cohgent-db:5432/omop"
```
>**Note:** When networking between Docker containers on a shared network as is defined for this project, the internal communication can happen directly by the service name as shown (`cohgent-db`) rather than the URL exposed externally to the host. This allows any parts of a compose deployment which do not need to be exposed outside of the Docker network to communicate while remaining hidden to the host system. For loading a database like these from the host system, which will be shown in the section of this document on setting up the OMOP CDM database, you will need to use the exposed localhost port rather than the service-name shown here.

If you update the example username or password in the `compose.yaml` for the services, you must also update them in the connection strings. **Please be aware that it is not recommended to use sensitive passwords in this way on non-secure systems, and as this deployment is built to be a local non-sensitive demo everything is stored in plain strings. Please do not use personal passwords or anything else that is not suitable to be stored as a plain, unencoded string.**

Ports may be configured through the `compose.yaml` file, but changes must be reflected in both the `local.env` (for databases) and `local.ui-config.json` (for the backend service API). Port conflicts with existing software running on a host machine are likely the most common cause of failure when running Docker Compose. This Compose file attempts to use non-default ports for what is exposed to the host machine to avoid this issue, except for with the UI given it is most users' point of entry and it is easier to load the site in a browser without having to go to a non-standard port.

For each service, the ports are specified as follows (the example given is for the backend service/API):
```
    ports:
      - "8500:8000"
```
This means that the external hostport `8500` maps to the internal container port of `8000`. Here, `8000` is the common default we are attempting to avoid. (Inside the container there are is nothing else running and so there are conflicts.) These are all accessed through the `http://localhost` URL in the host machine networking, meaning that to access to the running backend service directly you could go to `http://localhost:8500` (which will in fact be what the web browser uses when you load the frontend later). THE UI's default host port of 80 is the default port for `http` as a whole, meaning that `http://localhost` will suffice to load the frontend once deployed. If you need to change the ports for any reason, such as if Docker reports an error when running the file, you should only change the first of the two numbers, and use that to connect instead. For example, if you change the UI's `80:80` port mapping to `85:80` you would then connect to the UI by going to `http://localhost:85`.

#### Step 3 - Setup OMOP CDM

For more information on loading the OMOP Common Data Model database, please see the non-docker deployment instructions. The instructions are the same for both approaches as it is not loaded by the Docker Compose. This step is optional for basic functions, but required to use the Terminology Search features in the UI.

#### Step 4 - Run Docker Compose

Once you have the frontend code downloaded and all configuration setup to your liking, you can start the application by running the following command from the project root folder with Docker running:

```
docker compose up
```

This will deploy the database, then build and startup the API and UI. The API will then (on first load, or on all loads if `FORCE_RESEED = True`) create all tables for the main `cohgent-db`'s `cohgent` table, as well as load the observation value presets into the database. Once all three are running, you should be able to access the UI by going to `http://localhost` in your browser (or if you changed your port to something besides `80` above, whatever port you used).

Note that to bring the software stack down later, you may use:

```
docker compose down
```
#### Dockerfile Notes

The CohGenT API Backend includes two Dockerfiles: `Dockerfile` and `Dockerfile.local`. The only difference between these is that `Dockerfile` was built for pipelines where the `.env` file must be copied into the container image directly or for which volume mounting of the `.env` file is not available. `Dockerfile.local` removes this one command to match the approach used by the Docker Compose deployment provided, instead preferring to use the local volume mounting for the `.env` file as discussed.

### Non-Docker Deployment

This section provides a more detailed step-by-step including the OMOP CDM database instructions.

#### Step 1 - Stand up Databases

Requirements
- A SQL Database Server (see notes about SQL Alchemy below) and at least one database
- Database Management tool of choice (the PSQL CLI, DataGrip, etc.) to load DDLs and CSVs

As there are key dependencies for the databases, the first step that must be undertaken is setting up your database server(s) of choice. 

The CohGenT API requires a SQL database for some core functionality and expects it to exist on startup of the backend service. It also allows for an optional OMOP Common Data Model database to enable searching for healthcare terminology (ICD10, SNOMED, LOINC, etc). Please be aware that while the CohGenT API does not require the terminology database, the UI assumes it exists because of user facing expectations (e.g., quality of life features). If you are using the stack in its entireity, assume the OMOP database is also required to avoid any UI confusion or errors. The OMOP database must come prebuilt due to its complexity, with all expected concepts loaded.

>**IMPORTANT NOTE: This project uses SQL Alchemy to make database support simpler, but has only been tested explicitly with SQLite and Postgres. Please review the SQL Alchemy documentation and feature list for information on supported databases at [https://www.sqlalchemy.org/features.html](https://www.sqlalchemy.org/features.html). You may also need to install appropriate database drivers for Python.**

##### Setting up the Main Application Database

For the main application database, the CohGenT API will build the appropriate tables on startup and no additional configuration is required. It will also seed the preset value table with the list of common lab tests found [here](./data/lab_value_presets.csv). This list is only loaded if the table is empty. To rebuild the database table, launch the backend API with the FORCE_RESEED flag set to True, though be aware **this is a destructive action** and will clean the entire table, including for presets added by users through the API. Before forcing a reseed, it is recommended to back up the tables.

The internal CohGenT Database provides the backbone for the application features, predominantly the Lab Value Presets and the settings samples in this version. This database is required for the application to function in order to maintain alignment with the UI expectations.

The lab value preset tables are seeded on startup with values for common CBC and CMP lab tests. For more information on the tests included in the starter set, please see the complete documentation. Also, see the maintaining the lab preset seed section of this documentation for more information on adding to the starter set or reseeding the database in case of error.

##### Setting up the OMOP Common Data Model Database

> Note: For general information on the OMOP CDM, please see the related OMOP CDM overview section at the start of this README.

Setting up the OMOP CDM database has several requirements. The first is you will want to have an API Key from the National Library of Medicine's Unified Medcial Language System (UMLS). This is to build concepts related to the CPT4 terminology system due to licensing. (There is no cost involved with this.) You can register a UMLS account at: [https://uts.nlm.nih.gov/uts/](https://uts.nlm.nih.gov/uts/). Please follow the instructions there to register and obtain an API Key.

Once you have an API Key (or while you are waiting for it), proceed to the OHDSI Athena website at: [https://athena.ohdsi.org/](https://athena.ohdsi.org/). This is where you will download a set of the terminology systems you will load into the database later. This process may take a while for the download to be compiled, so it is recommended to do this part early.

Once you are at the Athena website, you may need to register an account. Once you have done so and are logged in, click the "Download" button in the top right corner.

This will bring up a list of all the available systems. For CohGenT, select the following:
* ICD10CM    International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS)
* ICD10PCS    ICD-10 Procedure Coding System (CMS)
* ICD10    International Classification of Diseases, Tenth Revision (WHO)
* Race    Race and Ethnicity Code Set (USBC)
* Gender    OMOP Gender
* NDC    National Drug Code (FDA and manufacturers)
* RxNorm    RxNorm (NLM)
* LOINC    Logical Observation Identifiers Names and Codes (Regenstrief Institute)
* CPT4    Current Procedural Terminology version 4 (AMA)
* SNOMED    Systematic Nomenclature of Medicine - Clinical Terms (IHTSDO)

Once you have them selected, click the "Download Vocabularies" button in the top right. This will begin preparing the download, which should send a notification to the registered email when it is ready.

Once you have your set of downloaded vocabularies, extract the zip file into a folder. There will be a set of CSV files used to populate the database tables along with a set of files related to CPT4. The CPT4 files include scripts to add the CPT4 concepts to the relevant CSVs. Please read the included README file for the scripts to confirm, but as of this writing you will run the command (for linux):
```
./cpt.sh {your_umls_api_key}
```

When this is complete, your files will be ready to load into your database once the schema is setup.

To build the OMOP CDM tables, the official OHDSI one is to go to their GitHub repositority and follow instructions at: [https://github.com/OHDSI/CommonDataModel](https://github.com/OHDSI/CommonDataModel). This includes tooling to generate schemas for various databases, though also has pre-generated DDLs available. Note that this application uses the current standard of 5.4 (any minor version should be fine).

For an example, you may also look at the docker image designed for Health Informatics students maintained by the developer of this application at: [https://github.com/SmartChartSuite/OMOP-5.4-PostgreSQL](https://github.com/SmartChartSuite/OMOP-5.4-PostgreSQL). This repository includes the DDLs and a load vocabulary script, which we will reference again in a moment.

Once you have your DDLs and a running database, you will want to use the tool of your choice to actually build the OMOP CDM tables. It is recommended to start by only running the core schema DDL initially (not the indices/constraints) to speed up loading of the Athena CSVs. (**Warning: This may be error prone if you are not sure what you are doing, in which case loading the constraints/etc. first might make the process take longer but would be generally safer.**) Precise instructions will vary depending on your database server and other tools.

For an example based on the previously discussed docker image scripts as a baseline, for the Postgres CLI client connecting to a Postgres database would run something like:
```
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER"
    CREATE DATABASE omop54;
    \c omop54
    \i /scripts/OMOPCDM_postgresql_5.4_ddl.sql
```

Once the tables are built (regardless of whether you added the constraints/etc. yet), you can load the prepared Athena CSVs. There are two very important, non-standard considerations to be aware of with these CSVs:
1. Athena uses tab (`'\t'`) delimitation instead of comma delimitation.
2. Many medical descriptions include quotation marks in unusual ways (e.g., for measurements), so a non-standard character should be set. (The recommended character is `'\b'`, or backspace, which doesn't occur in the data.)

In addition, it should be noted they include a CSV Header row for tools that assume a default of no header.

The linked docker image repository includes a `load_vocabulary.sql` script which demonstrates the use of the PSQL CLI to load the database with these requirements:
```
\COPY CONCEPT FROM '/VOCAB/CONCEPT.csv' WITH DELIMITER E'\t' CSV HEADER QUOTE E'\b' ;
```
This sets the delimiter to tab, sets the header, and the quote charcter to backspace when performing the COPY.

If there is a failure while loading the database, it is generally recommended to clear it and start again if the precise point of failure is not known.

#### Step 2 - Backend Service API

Requirements:
* Python 3.12+ (Slightly older versions may work, but the application was built assuming 3.12 and so should not be trusted.)
* Conda or another Python virtual environment manager
* Hypercorn or another Python web server

To get started deploying the CohGenT backend service, it is recommended to use a python virtual environment such as Venv or Conda for this application. Please follow instructions to setup and enter your environment based on your tool of choice. Conda is generally recommended. Conda documentation can be found at [https://docs.conda.io/en/latest/](https://docs.conda.io/en/latest/). For lightweight Conda, you can use Miniforge, which provides minimal installers. You can find Miniforge at [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge).

Once you have a virtual environment configured and you are have activated it, you can install all dependencies from the project root folder with:
```
pip install -f requirements.txt
```
This includes drivers for Postgres only, if you are using another database you should install all required drivers for it as well via `pip install`.

After you have the environment setup, you should configure the application's variables. Start by creating a `.env` file within the project root folder based on the `example.env` file (or simply rename that file and fill it in). For more information on the variables, please see the appropriate section of this document. The application uses the Pydantic Settings library to read directly from the `.env` file, so no additional application configuration is required. (Note that for an API only deployment, you can deploy without a working OMOP database. Leaving the string empty will disable the related router, and allow you to do deployment testing without the burden.)

Next, you must select a web server in order to deploy the backend code. This may vary by the host machine, but for Linux it is recommended to serve the API using Uvicorn or Hypercorn, which are ASGI Web Servers for Python applications. Hypercorn is installed automatically by the previous step.

* For more information on Uvicorn, please see their official documentation at: [https://uvicorn.dev/](https://uvicorn.dev/).
* For more information on Hypercorn, please see their official documentation at: [https://hypercorn.readthedocs.io/en/latest/](https://hypercorn.readthedocs.io/en/latest/).

Both are considered high end options and come with a number of features which may be set. For this documentation, we will give a bare minimum example using Hypercorn.

From the project folder, you may run the following command:
```
hypercorn api.main:app
```
This will start the Hypercorn server from the module `api.main`. What this means in plain terms is that in the `./api/` folder it will run the `main.py` file. If the file structure is named or it is running from a different location, this should be adjusted. The `:app` refers to the specific FastAPI instance inside the `main.py` file.

Using default settings, this should stand the API up at `http://localhost:8000`. You can test this by going to `http://localhost:8000/info`.

> Note: Setting this up to run through NGINX or other is outside the scope of this documentation. For cloud services, it is recommended to look at the official FastAPI documentation at [https://fastapi.tiangolo.com/deployment/cloud/](https://fastapi.tiangolo.com/deployment/cloud/).

#### Step 3 - Frontend UI

Requirements:
* Node 22+
* Angular CLI 21+
* NGINX or similar web server

The CohGenT Frontend UI is an Angular Typescript project and must be built into static HTML and Javascript, then deployed into a webserver such as NGINX. Instructions here will be given for NGINX as an example. There are three big configuration items prior to the build:

* The "Base HREF" path - The path to which the frontend will be deployed that must be set in both in the Angular build and in the NGINX configuration.
* API Url - The base URL for the Backend Service/API.
* Contact Email - The email to use for the contact and report issue buttons.

The "Base HREF" is a build argument for the Angular CLI, while the other two are set in the `config.json` file which will be placed in the UI's assets folder. Base HREF works by replacing relevant paths in the codebase for compiling the static HTML/JS. If you intend to deploy on the domain/subdoman root such as `http://cohgent.example.com/` the base HREF would be empty or `/`. If you were to deploy on a non-base path such as `http://example.com/cohgent/` the base HREF would be `/cohgent/`.

To perform a production build, you will need to have Node and the Angular CLI installed. Node version should be at least version 22. It is recommended to use the Node Version Manager tool for this, but not required. Node Version Manager (NVM) can be found at [https://github.com/nvm-sh/nvm](https://github.com/nvm-sh/nvm). NVM helps manager Node environments.

To begin building the UI, navigate into the root of the UI project folder. First, install all dependencies with:
```
npm install
```

Once the dependencies are fully install you can build using the angular CLI as follows, adding the base HREF if needed replacing `/path/` with where you are deploying:
```
ng build
-- OR --
ng build --base-href=/path/
```

This will compile the static assets into the `./dist/cohort-generation-ui/` folder. In this folder there is a text file documenting any third party licenses, and a `/browser/` folder that has the static assets which should look like the following:
```
/dist/cohort-generation/ui/browser/
├── favicon.ico
├── index.html
├── main-#.js
├── polyfills-#.js
├── styles-#.css
└── assets/
    └── config/
        └── config.json
```

You will need to copy these files into the webserver of your choice per the server's instructions. For NGINX, the default path would be `/usr/share/nginx/html/` or`/usr/share/nginx/html/your_base_href_path/`.

The most notable file here is the `/assets/config/config.json`. This is a browser run time (when the application is loaded into the browser from the web server) configuration file. This file should be edited to set the API URL (the base endpoint of the backend service API) and the contact e-mail address. Note that contact e-mail is actually optional, if it is not provided the contact and report issue buttons will be disabled in the UI.

You will also need to edit the `nginx.conf` file for your NGINX server and add an entry for the CohGenT UI. A very simple example is as follows (no security headers or other options):
```
server {
  listen 80;
  root /usr/share/nginx/html;
  location / {
      # alias /usr/share/nginx/html/;
      try_files $uri $uri/ ${BASE_HREF}index.html;
      
      # Handle index explicitly
      index index.html;
  }
}
```
Location should be set to match the base HREF specified in the build (e.g., `location /cohgent/`).

To summarize, if you are deploying at a non-domain root path, fyou **must** match the path in the following locations (assuming NGINX, though most servers will have equivalents):
1. The build command's base-href argument.
2. The server's static HTML/JS folder path. (For NGINX, the `/usr/share/nginx/html/{your_path_here}` folder.)
3. The server's configuration file's path. (For NGINX, `nginx.conf` location.)


## Information for Contributors and Maintainers

This section of the documentation discusses a number of core design aspects for the CohGenT backend service intended for open source contributors and codebase maintainers.

### General Application Workflow

TODO

### Type Support
FHIR Type support is limited in the current version of the application, based around what was defined for the existing scenarios. Typing is a complex alignment between the user input, the generation requirements, and the expected FHIR Sheets formatting. For example, the internal typing provides for a "ValueCoding" type in Pydantic which handles a combination of system, code, and display strings and is allowed input to generate either the FHIR Coding or CodeableConcept types. When building or modifying a scenario, failure to align allowed input types to the FHIR type will cause an error in processing.

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

Note that "HumanName" is a special field and considered always randomly generated. For more information, see the special values listed further down.

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

Some other special values ($) are present but do not have special functions attached to them, and are only to meet validation requirements for certain user configured fields. These should be disregarded.

## Generation Module
The Generation Module is an internal component which provides the actual data generation for a given set of user settings and scenario. The output of the Generation Module are the FHIR Sheets input models, which are representative of a spreadsheet input processed by the FHIR Sheets library. Entities are defined external to the main "table" (in a specific page of a spreadsheet in the CLI version of FHIR Sheets), while each "column" in the main table is a single field within an entity. For example, the entity definitions will lay out something like the "US Core 6.1.0 Patient" profile, while a single column in the main data table will be the `Patient.birthdate` field for that entity.

### Special Fields
While most fields are intended to be handled dynamically, there are a few important exceptions. Foremost among these are the primary event date for a given patient, the patient's name, the patient's gender (`Patient.gender`), and the demographic distributions for all patients. Primary event date is used to set the baseline date for all of the patient's records. Gender is used as a depedency to generate names.

### Resource References
For every resource which has a main subject/patient reference, this is defined specifically in the entity model by the `referencePath` field. For most resources, this is simply `subject` (the resource type is not required as with other FHIR Paths). Additional references to other entities may be defined in the `otherReferences` field, which list of objects including `referencePath` and `target` (the entity the reference should be to).

For example, in the Condition Based Record scenario, the PrimaryEncounter entity (U.S. Core Encounter profile) includes a `reasonReference` to the PrimaryCondtion (U.S. Core Encounter Diagnosis Condition profile) as shown in addition to it's primary subject/patient reference:
```
            "referencePath": "subject",
            "otherReferences": [
                {
                    "referencePath": "reasonReference",
                    "targetEntity": "PrimaryCondition"
                }
            ],
```

Note that entities defined this way are generally non-repeating, and so further configuration of references is not required.

For iterative generation, such as repeating lab observations, in Event Sets there is special handling when the containing DiagnosticReport is enabled (for Lab Panels, specifically the U.S. Core DiagnosticReport Lab Results profile). In this case, the references to the contained member resources are generated automatically. (TODO ADD MORE INFO ON VENT SETS)

## Lab Value Presets

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

## Sample Settings

TODO
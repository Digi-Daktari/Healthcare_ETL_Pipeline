# Healthcare ETL Pipeline

A Python-based ETL pipeline for cleaning and transforming messy healthcare data into a structured, analysis-ready dataset.

## Project Overview

This project simulates a real-world data engineering task for **MedCore Analytics**, supporting **St. Aurelius General Hospital**.

The source dataset contains patient, appointment, and billing records with common data quality issues such as missing values, duplicate rows, invalid values, and inconsistent data types. This ETL pipeline extracts the raw data, validates and cleans it, applies transformations, and outputs a processed dataset ready for reporting or analysis.

## Role

**Data Engineer**

## Problem Statement

Healthcare organizations often receive raw operational data that is not immediately usable for analytics. Before the data can support dashboards, reporting, or modeling, it must be cleaned and standardized.

This project addresses that problem by building a repeatable pipeline that prepares healthcare data for downstream use.

## Features

- Loads raw healthcare data from CSV files
- Removes duplicate records
- Handles missing and invalid values
- Standardizes column names and data types
- Validates records before processing
- Saves cleaned output data
- Includes tests for pipeline reliability
- Uses environment variables for configurable settings

## Project Structure

```text
Healthcare_ETL_Pipeline/
|
|-- data/
|   |-- raw/
|   |   `-- raw-data.csv
|   `-- processed/
|       `-- processed-data.csv
|
|-- sql/
|
|-- src/
|   `-- pipeline source code
|
|-- tests/
|   `-- test files
|
|-- config.py
|-- run.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- README.md
```

## Input and Output

**Input file:**

```text
data/raw/raw-data.csv
```

**Output file:**

```text
data/processed/processed-data.csv
```

## Technologies Used

- Python
- Pandas
- Pytest
- PostgreSQL / Supabase connection configuration
- Environment variables

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Digi-Daktari/Healthcare_ETL_Pipeline.git
cd Healthcare_ETL_Pipeline
```

### 2. Create a virtual environment

```bash
python -m venv hc-etl-pipeline
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\hc-etl-pipeline\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source hc-etl-pipeline/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file using `.env.example` as a guide:

```bash
cp .env.example .env
```

Then update the values in `.env` with your own database credentials and schema settings.

> Do not commit the `.env` file to GitHub. It may contain private credentials.

## Running the Pipeline

Run the ETL pipeline with:

```bash
python run.py
```

After the pipeline runs successfully, the cleaned dataset will be saved to:

```text
data/processed/processed-data.csv
```

## Running Tests

To run the test suite:

```bash
pytest
```

## Environment Variables

The project uses environment variables such as:

```text
DB_URL
INDUSTRY
LEARNER_SCHEMA
```

Example values are provided in `.env.example`.

## Data Quality Tasks Performed

The pipeline is designed to handle common healthcare data issues, including:

- Null or missing values
- Duplicate records
- Invalid dates
- Incorrect data types
- Impossible numeric values
- Inconsistent formatting

## Expected Outcome

The final output is a cleaned healthcare dataset that can be used for:

- Business intelligence dashboards
- Reporting
- Data analysis
- Machine learning preparation
- Database loading

## Author

**Digi-Daktari**

## Repository

```text
https://github.com/Digi-Daktari/Healthcare_ETL_Pipeline
```

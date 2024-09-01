# Kobo Extraction System Documentation

## Table of Contents
- [Kobo Extraction System Documentation](#kobo-extraction-system-documentation)
  - [Table of Contents](#table-of-contents)
  - [1. System Overview](#1-system-overview)
  - [2. System Architecture](#2-system-architecture)
  - [3. Setup Instructions](#3-setup-instructions)
  - [4. Usage Guide](#4-usage-guide)
    - [Extracting Data](#extracting-data)
    - [Viewing Data Quality Issues](#viewing-data-quality-issues)
    - [Accessing Analytics](#accessing-analytics)
    - [Webhook for Real-time Updates](#webhook-for-real-time-updates)
  - [5. Database Schema](#5-database-schema)
  - [6. API Documentation](#6-api-documentation)
    - [Kobo Extraction Endpoints](#kobo-extraction-endpoints)
    - [Data Quality Endpoints](#data-quality-endpoints)
    - [Analytics Endpoints](#analytics-endpoints)
  - [7. Data Quality Checks](#7-data-quality-checks)
  - [9. Cron Jobs](#9-cron-jobs)
  - [10. Testing](#10-testing)
  - [11. Troubleshooting](#11-troubleshooting)

## 1. System Overview

The Kobo Extraction System is designed to extract data from KoboToolbox, process it, and store it in a local database. It provides real-time updates through webhooks, performs data quality checks, and offers analytics on the extracted data.

Key Features:
- Data extraction from KoboToolbox API
- Real-time updates via webhooks
- Data quality checks
- Scheduled daily extractions

## 2. System Architecture

<antArtifact identifier="system-architecture" type="application/vnd.ant.mermaid" title="System Architecture Diagram">
graph TD
    A[KoboToolbox API] --> B[KoboDataService]
    B --> C[KoboExtractionService]
    C --> D[Database]
    E[Webhook] --> F[WebhookController]
    F --> C
    G[Cron Job] --> B
    H[DataQualityService] --> D
    I[AnalyticsService] --> D
    J[API Endpoints] --> H
    J --> I
    J --> C


## 3. Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/kobo-extraction-system.git
   cd kobo-extraction-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   KOBO_API_TOKEN=your_kobo_api_token
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

5. Initialize the database:
   ```
   alembic upgrade head
   ```

6. Start the application:
   ```
   uvicorn src.main:app --reload
   ```

## 4. Usage Guide

### Extracting Data
- To manually trigger a data extraction, send a GET request to `/kobo-extraction/extract`
- The system will automatically extract data daily using a cron job

### Viewing Data Quality Issues
- Send a GET request to `/data-quality/issues` to view current data quality issues
- To run a new data quality check, send a POST request to `/data-quality/check`

### Accessing Analytics
- Various analytics endpoints are available under `/analytics/`
- For example, `/analytics/survey-statistics` provides statistics about surveys

### Webhook for Real-time Updates
- Set up a webhook in KoboToolbox pointing to `/kobo-extraction/webhook`
- The system will process incoming data in real-time

## 5. Database Schema

```mermaid
erDiagram
    SURVEY ||--o{ CLIENT : has
    SURVEY {
        int id
        string survey_id
        uuid form_uuid
        datetime start_time
        datetime end_time
        date survey_date
        string unique_id
        datetime submission_time
        string version
        uuid instance_id
        string xform_id_string
        string status
        float latitude
        float longitude
    }
    CLIENT ||--o{ BUSINESS : owns
    CLIENT {
        int id
        string name
        string id_manifest
        string location
        string phone_primary
        string phone_secondary
        string phone_type
        string gender
        int age
        string nationality
        string strata
        boolean has_disability
        string education
        string client_status
        boolean is_sole_income_earner
        int dependents
    }
    BUSINESS {
        int id
        string client_id_manifest
        string status
        string is_operating
    }
    BDA ||--o{ SURVEY : conducts
    BDA {
        int id
        string name
        string country_name
        string region_name
    }
    COHORT ||--o{ SURVEY : belongs_to
    COHORT {
        int id
        string name
    }
    PROGRAM ||--o{ SURVEY : belongs_to
    PROGRAM {
        int id
        string name
    }
    COUNTRY ||--o{ REGION : has
    COUNTRY {
        int id
        string name
    }
    REGION {
        int id
        string name
        int country_id
    }
    NATIONALITY ||--o{ CLIENT : has
    NATIONALITY {
        int id
        string name
    }
    ISSUE {
        int id
        string entity_type
        string issue_type
        string entity_id
        json details
        datetime created_at
    }

```

## 6. API Documentation

### Kobo Extraction Endpoints
- `GET /kobo-extraction/extract`: Triggers a manual data extraction
- `POST /kobo-extraction/webhook`: Endpoint for KoboToolbox webhook

### Data Quality Endpoints
- `GET /data-quality/issues`: Retrieves current data quality issues
- `POST /data-quality/check`: Runs a new data quality check

### Analytics Endpoints
- `GET /analytics/survey-statistics`: Retrieves survey statistics
- `GET /analytics/client-statistics`: Retrieves client statistics
- `GET /analytics/business-statistics`: Retrieves business statistics

## 7. Data Quality Checks

The system performs the following data quality checks:
- Missing required fields
- Invalid data formats (e.g., dates, UUIDs)
- Logical inconsistencies (e.g., end time before start time)
- Data range validations (e.g., age limits)
- Duplicate entries

## 9. Cron Jobs

A daily cron job is set up to:
- Extract new data from KoboToolbox
- Perform data quality checks
- Update analytics

To modify the cron schedule, edit the `crontab` file:
```
0 0 * * * /path/to/your/python /path/to/your/script.py
```

## 10. Testing

Run the test suite using pytest:
```
pytest
```

The test suite includes:
- Unit tests for all services
- Integration tests for database operations
- API endpoint tests
- Data quality check tests

## 11. Troubleshooting

Common issues and their solutions:
- API Connection Errors: Check your internet connection and verify the API token
- Database Errors: Ensure the database is running and the connection string is correct
- Webhook Errors: Verify the webhook URL in KoboToolbox settings

For further assistance, please open an issue on the GitHub repository.

</antArtifact>

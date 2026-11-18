# Task 1: Baserow to ClickHouse Data Ingestion

## Project Overview

This project implements a Python-based data ingestion pipeline that retrieves records from Baserow and loads them into ClickHouse.

The script supports API pagination, environment-based configuration, data transformation, and safe snapshot replacement.

## Objectives

- Fetch all records from Baserow using its REST API.
- Handle pagination to retrieve all available records.
- Store the data in a ClickHouse database.
- Keep the ten business fields as String columns.
- Support repeatable ingestion without duplicate records.
- Keep credentials outside the source code.

## Technology Stack

- Python
- Baserow REST API
- ClickHouse
- Requests
- clickhouse-connect

## Project Structure

```text
task-1-baserow-clickhouse/
├── mea_baserow_to_clickhouse.py
├── .env.example
├── requirements.txt
├── README.md
└── screenshots/
```

## Database Design

**Database:** `mea_agreement`

**Table:** `agreements`

The table stores the Baserow row ID, ten business fields, and an ingestion timestamp.

## How It Works

1. Connects to Baserow using an API token stored in an environment variable.
2. Retrieves records from all available API pages.
3. Transforms the records into the required ClickHouse column structure.
4. Creates the database and table if they do not already exist.
5. Replaces the previous snapshot and inserts the latest records.

## Local Testing

The script includes a fictional test-data mode, allowing the pipeline to be tested without access to company credentials or production data.

Run:

```bash
python mea_baserow_to_clickhouse.py --use-fake-data
```

### Test Results

- Four fictional records inserted successfully.
- Repeated execution completed successfully.
- Final row count remained four.
- No duplicate records were created by repeated execution.

**Note:** Live Baserow API ingestion has not been tested because production API credentials were not provided. The local demonstration uses fictional data.

## Environment Variables

Configure the following variables before running the actual ingestion:

- `BASEROW_TOKEN`
- `CLICKHOUSE_HOST`
- `CLICKHOUSE_HTTP_PORT`
- `CLICKHOUSE_USER`
- `CLICKHOUSE_PASSWORD`

Never commit real credentials or `.env` files.

## Execution

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the local demonstration:

```bash
python mea_baserow_to_clickhouse.py --use-fake-data
```

Run actual ingestion only after configuring authorized Baserow and ClickHouse credentials:

```bash
python mea_baserow_to_clickhouse.py
```

## Project Status

Local demonstration completed and verified successfully.

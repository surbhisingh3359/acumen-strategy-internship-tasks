
import os
import argparse
import logging
from typing import Any

import requests # pyright: ignore[reportMissingModuleSource]

try:
    import clickhouse_connect  # pyright: ignore[reportMissingImports]
except ImportError:
    clickhouse_connect = None


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASEROW_API_URL = (
    "https://b4s3r0w.acm.acumen-strategy.com/"
    "api/database/rows/table/2649/"
)

TABLE_NAME = "mea_agreement.agreements"

COLUMNS = [
    "baserow_row_id",
    "unit",
    "reporting_month",
    "data_item",
    "owner",
    "monthly_target",
    "data_source",
    "submission_frequency",
    "agreement_status",
    "agreed_by",
    "agreed_date",
]

BASEROW_FIELDS = [
    "unit",
    "reporting_month",
    "data_item",
    "owner",
    "monthly_target",
    "data_source",
    "submission_frequency",
    "agreement_status",
    "agreed_by",
    "agreed_date",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# CLICKHOUSE CONNECTION
# --------------------------------------------------

def get_clickhouse_client():
    """Connect to the local ClickHouse server."""

    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "analytics_user"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
    )


# --------------------------------------------------
# CREATE DATABASE AND TABLE
# --------------------------------------------------

def create_table(client):
    """Create the MEA database and agreements table."""

    client.command("CREATE DATABASE IF NOT EXISTS mea_agreement")

    client.command("""
        CREATE TABLE IF NOT EXISTS mea_agreement.agreements
        (
            baserow_row_id        UInt32,
            unit                  String,
            reporting_month       String,
            data_item             String,
            owner                 String,
            monthly_target        String,
            data_source           String,
            submission_frequency  String,
            agreement_status      String,
            agreed_by             String,
            agreed_date           String,
            ingested_at           DateTime DEFAULT now()
        )
        ENGINE = MergeTree
        ORDER BY (unit, reporting_month)
    """)

    logger.info("Database and table are ready.")


# --------------------------------------------------
# FETCH DATA FROM BASEROW
# --------------------------------------------------

def fetch_baserow_data():
    """Fetch all rows by following Baserow pagination."""

    token = os.getenv("BASEROW_TOKEN")

    if not token:
        raise ValueError(
            "BASEROW_TOKEN is missing. "
            "Set it as an environment variable before running."
        )

    headers = {
        "Authorization": f"Token {token}"
    }

    next_url = BASEROW_API_URL
    params = {
        "user_field_names": "true",
        "size": 200,
    }

    all_rows = []
    visited_urls = set()

    with requests.Session() as session:

        while next_url:

            if next_url in visited_urls:
                raise RuntimeError("Repeated pagination URL detected.")

            visited_urls.add(next_url)

            response = session.get(
                next_url,
                headers=headers,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            page = response.json()

            if "results" not in page:
                raise ValueError(
                    "Unexpected Baserow response: 'results' is missing."
                )

            all_rows.extend(page["results"])

            logger.info(
                "Fetched %s rows. Total so far: %s",
                len(page["results"]),
                len(all_rows),
            )

            next_url = page.get("next")

            # Parameters are already included in the next URL.
            params = None

    logger.info("Total Baserow rows fetched: %s", len(all_rows))

    return all_rows


# --------------------------------------------------
# FAKE DATA FOR LOCAL TESTING
# --------------------------------------------------

def get_fake_data():
    """Return fictional rows for local testing only."""

    return [
        {
            "id": 1,
            "unit": "MEA Unit A",
            "reporting_month": "2026-10",
            "data_item": "Customer Satisfaction",
            "owner": "Test Owner A",
            "monthly_target": "90",
            "data_source": "Internal Report",
            "submission_frequency": "Monthly",
            "agreement_status": "Agreed",
            "agreed_by": "Test Manager A",
            "agreed_date": "2026-10-01",
        },
        {
            "id": 2,
            "unit": "MEA Unit A",
            "reporting_month": "2026-10",
            "data_item": "Revenue",
            "owner": "Test Owner B",
            "monthly_target": "50000",
            "data_source": "Finance Report",
            "submission_frequency": "Monthly",
            "agreement_status": "Agreed",
            "agreed_by": "Test Manager B",
            "agreed_date": "2026-10-02",
        },
        {
            "id": 3,
            "unit": "MEA Unit B",
            "reporting_month": "2026-10",
            "data_item": "New Customers",
            "owner": "Test Owner C",
            "monthly_target": "100",
            "data_source": "CRM",
            "submission_frequency": "Monthly",
            "agreement_status": "Pending",
            "agreed_by": "",
            "agreed_date": "",
        },
        {
            "id": 4,
            "unit": "MEA Unit B",
            "reporting_month": "2026-10",
            "data_item": "Projects Completed",
            "owner": "Test Owner D",
            "monthly_target": "20",
            "data_source": "Project Tracker",
            "submission_frequency": "Monthly",
            "agreement_status": "Agreed",
            "agreed_by": "Test Manager D",
            "agreed_date": "2026-10-03",
        },
    ]


# --------------------------------------------------
# TRANSFORM BASEROW ROWS
# --------------------------------------------------

def transform_rows(baserow_rows):
    """Convert Baserow records into ClickHouse insert rows."""

    transformed = []

    for row in baserow_rows:

        row_id = row.get("id")

        if row_id is None:
            raise ValueError("A Baserow row is missing its ID.")

        values = [int(row_id)]

        for field in BASEROW_FIELDS:
            value = row.get(field)

            # Store all ten business fields as strings.
            values.append("" if value is None else str(value))

        transformed.append(tuple(values))

    return transformed


# --------------------------------------------------
# LOAD DATA INTO CLICKHOUSE
# --------------------------------------------------

def load_into_clickhouse(client, rows):
    """Replace the previous snapshot with the newly fetched data."""

    # All source rows are fetched and transformed before this point.
    # Therefore, an API failure will not erase existing table data.

    client.command(f"TRUNCATE TABLE {TABLE_NAME}")

    if rows:
        client.insert(
            TABLE_NAME,
            rows,
            column_names=COLUMNS,
        )

    logger.info("Successfully loaded %s rows.", len(rows))


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Baserow to ClickHouse MEA ingestion script"
    )

    parser.add_argument(
        "--use-fake-data",
        action="store_true",
        help="Use fictional data for local testing.",
    )

    args = parser.parse_args()

    try:

        logger.info("Starting MEA ingestion process.")

        # Fetch the data before changing the ClickHouse table.
        if args.use_fake_data:
            logger.info("Using fictional test data.")
            baserow_rows = get_fake_data()
        else:
            logger.info("Fetching data from Baserow.")
            baserow_rows = fetch_baserow_data()

        rows = transform_rows(baserow_rows)

        client = get_clickhouse_client()

        try:
            create_table(client)
            load_into_clickhouse(client, rows)
        finally:
            client.close()

        logger.info("MEA ingestion completed successfully.")

    except Exception:
        logger.exception("MEA ingestion failed.")
        raise


if __name__ == "__main__":
    main()

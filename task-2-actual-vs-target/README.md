# Task 2 — Actual vs Target dbt Models

## Objective
Compare MEA monthly targets with actual performance using dbt and ClickHouse.

## Models
1. `stg_mea_unit_a__actuals.sql`
   - Reads fictional actuals from the local ClickHouse source.
   - Standardizes unit, reporting month, data item, and actual value.

2. `fct_mea_actual_vs_target.sql`
   - Reads targets from `mea_agreement.agreements`.
   - Uses `ref()` to access the staging model.
   - Uses a LEFT JOIN to preserve targets without actuals.
   - Calculates `hit` or `miss` status.

## Local testing
All actuals used in local testing are fictional.
See `setup_fake_actuals.sql` for the test table setup.

Command:
`dbt build --select +fct_mea_actual_vs_target`

Results:
- Both models built successfully.
- All 7 data tests passed.
- Four target records returned.
- Two actuals matched; two targets had no actual.
- Rerunning the mart retained exactly four rows.

## Production handover
Replace the fictional source with the actual database, table,
and column names provided by the company.

The staging model belongs in the staging pipeline.
The mart requires routing through the appropriate MEA gold DAG
in the production Airflow repository.

-- Intentional failing test for validating Elementary webhook alerts.
-- This query returns one row, so dbt marks the test as failed.

select 1 as failure_id

{{ config(materialized='table', tags=['marts', 'mea']) }}

WITH targets AS (
    SELECT
        unit,
        reporting_month,
        data_item,
        toFloat64OrNull(monthly_target) AS target
    FROM {{ source('mea', 'agreements') }}
),

actuals AS (
    SELECT
        unit,
        reporting_month,
        data_item,
        actual_value
    FROM {{ ref('stg_mea_unit_a__actuals') }}
)

SELECT
    t.unit,
    t.reporting_month,
    t.data_item,
    t.target,
    a.actual_value AS actual,
    CASE
        WHEN isNull(a.actual_value) THEN 'miss'
        WHEN isNull(t.target) THEN 'miss'
        WHEN a.actual_value >= t.target THEN 'hit'
        ELSE 'miss'
    END AS status
FROM targets AS t
LEFT JOIN actuals AS a
    ON t.unit = a.unit
    AND t.reporting_month = a.reporting_month
    AND t.data_item = a.data_item
SETTINGS join_use_nulls = 1

{{ config(materialized='view') }}

SELECT
    'MEA Unit A' AS unit,
    reporting_month,
    data_item,
    actual_value
FROM {{ source('mea_unit_a', 'mea_unit_a_actuals') }}

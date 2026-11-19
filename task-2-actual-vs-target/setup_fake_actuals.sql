-- Fictional local test data only.
-- This table is not the company's production actuals source.

CREATE TABLE IF NOT EXISTS raw.mea_unit_a_actuals
(
    reporting_month String,
    data_item String,
    actual_value Float64
)
ENGINE = MergeTree
ORDER BY (reporting_month, data_item);

TRUNCATE TABLE raw.mea_unit_a_actuals;

INSERT INTO raw.mea_unit_a_actuals
    (reporting_month, data_item, actual_value)
VALUES
    ('2026-10', 'Customer Satisfaction', 92),
    ('2026-10', 'Revenue', 45000);

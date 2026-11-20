# Task 3: Elementary Webhook Alert Integration

## 1. Overview

This task demonstrates integrating Elementary with dbt to monitor data
quality test failures and send notifications to a Slack-compatible webhook.

A controlled failing dbt test is used to validate the alerting workflow.

## 2. Technology Stack

- Python 3.12
- dbt Core 1.12.7
- dbt-clickhouse 1.10.3
- Elementary 0.26.1
- ClickHouse
- Webhook.site for temporary testing

## 3. Architecture

1. dbt executes data quality tests.
2. Elementary captures dbt test execution results.
3. Elementary generates alerts from failed tests.
4. The Elementary CLI monitors generated alerts.
5. Alerts are delivered to a configured webhook endpoint.

## 4. Project Structure

\`\`\`text
task-3-elementary-webhook-alert/
├── README.md
├── requirements.txt
├── .env.example
├── dbt_project.yml
├── packages.yml
├── tests/
│   └── elementary_intentional_failure.sql
└── evidence/
\`\`\`

## 5. Configuration

The Elementary package is pinned to version 0.26.1 in packages.yml.

The webhook endpoint is supplied through the SLACK_WEBHOOK environment
variable. No webhook URL or database credentials are stored in source code.

The local dbt profile uses ClickHouse. Configure the Elementary CLI profile
to point to the Elementary metadata database and schema created by dbt.

## 6. Prerequisites

- Python 3.12
- ClickHouse instance
- Configured dbt profiles for the project and Elementary CLI
- Slack-compatible webhook endpoint

## 7. Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Install dbt packages:

```bash
dbt deps
```

## 8. Execution

Build Elementary models:

```bash
dbt run --select elementary --target dev
```

Run the intentional failing test:

```bash
dbt test --select elementary_intentional_failure --target dev
```

The test is expected to fail because its query returns one row.

Set the webhook URL securely in your terminal:

```bash
read -rsp "Webhook URL: " SLACK_WEBHOOK
echo
export SLACK_WEBHOOK
```

Run Elementary monitoring:

```bash
edr monitor --profile-target default --project-profile-target dev --slack-webhook "$SLACK_WEBHOOK" --days-back 7 --suppression-interval 0
```

## 9. Validation Results

- All 30 Elementary monitoring models built successfully.
- The intentional dbt test failed as expected.
- Elementary captured the failed test and generated an alert.
- The monitoring command reported one alert sent.
- Webhook.site received the alert for elementary_intentional_failure.
- The received alert showed status: fail.

## 10. Evidence

- `elementary-monitor-success.png`: successful monitoring output.
- `webhook-alert.png`: received notification showing the failed test.

## 11. Limitations

Webhook.site was used as a temporary Slack-compatible receiver to validate
alert delivery. This demonstrates webhook notification functionality but
does not represent a production Mattermost deployment.

A production integration requires the organization's actual Mattermost
webhook endpoint and credentials.

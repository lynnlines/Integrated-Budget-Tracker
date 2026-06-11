# Integrated Budget Tracker (Phase 1 scaffold)

This repository contains a Phase 1 scaffold for a portfolio-quality budget tracker backend.

## Quickstart

```bash
docker-compose up --build
```

App will be available at http://localhost:8000

## Setup

1. Configure `DATABASE_URL` in `.env` or environment variables. By default this app uses `sqlite:///./test.db` for local development.
2. Run migrations:

```bash
alembic upgrade head
```

3. Seed default categories and rules:

```bash
python -m app.db.seed
```

4. Optionally seed demo transactions:

```bash
python -m app.cli seed-demo
```

## OpenAPI docs and interactive API reference

When `ENABLE_DOCS=true`, the application exposes interactive documentation and the OpenAPI schema at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Set `ENABLE_DOCS=false` for production to disable interactive documentation.

Use these docs during development to inspect endpoint parameters, request bodies, and response schemas.

## Dashboard

The app includes a lightweight dashboard page for budget analytics and transaction history visualization.

- Visit the dashboard at `http://localhost:8000/dashboard`
- It loads current month summary metrics and a 6-month history from `/api/v1/summary/history`
- It also visualizes category spend breakdown from `/api/v1/summary/cache/monthly`

## Security and deployment notes

- Set `ENABLE_DOCS=false` for production to disable auto-generated Swagger and ReDoc endpoints.
- Set `TRUSTED_HOSTS` to a comma-separated allowlist of hostnames for `TrustedHostMiddleware`.
- Set `HTTPS_REDIRECT=true` in environments where TLS termination is required.

## Demo and CLI

The project includes a tiny CLI in `app/cli.py` for common developer/demo tasks.

- Seed demo transactions from `data/sample_transactions.csv`:

```bash
python -m app.cli seed-demo
```

- Print a curl command for the monthly summary endpoint:

```bash
python -m app.cli show-curl --year 2026 --month 6
```

- Refresh and print a monthly summary via the service layer:

```bash
python -m app.cli refresh-summary --year 2026 --month 6
```

Visit the dashboard at:

```bash
http://localhost:8000/dashboard
```

## Integrating your personal bank

This app is designed to automate transaction ingestion from a bank export.

Current bank integration path:

- Upload a CSV export from your personal bank account.
- Send it to the `/api/v1/transactions/import` endpoint.
- The backend parses the CSV using the `ChaseConnector` and applies rule-based categorization.

Example:

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/import" \
  -F "account_id=acct-1" \
  -F "file=@your-bank-export.csv"
```

Note:

- `account_id` is used to associate imported transactions with a bank account.
- The current connector is implemented for Chase-style CSV exports, but the architecture is built for additional bank connectors.
- To support another bank, add a new connector under `app/connectors/` and wire it into the import flow.

## Integrating Google Sheets

The app also supports importing transactions from Google Sheets via CSV export.

Options:

1. Upload a CSV-exported Google Sheet file:

```bash
curl -X POST "http://localhost:8000/api/v1/sheets/import" \
  -F "account_id=acct-1" \
  -F "file=@sheet.csv"
```

2. Send a public Google Sheets URL and let the service download the CSV export:

```bash
curl -X POST "http://localhost:8000/api/v1/sheets/import" \
  -F "sheet_url=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0" \
  -F "account_id=acct-1"
```

The backend uses `GoogleSheetsConnector` to download the sheet as CSV and normalize the rows.

## Notes on automation

This project is meant to automate the import and summary process, so the API endpoints are primarily integration points rather than manual user interfaces.

- Use the CLI and scheduled jobs for repeatable flows.
- Use direct endpoint calls only for onboarding, testing, or connecting a new data source.
- The system is built so you can later wire the same endpoints into a webhook, scheduler, or integration service.

## Future SaaS roadmap

A short SaaS roadmap is available in `FUTURE_SAAS.md`.

## Tests and coverage

Run the full test suite with coverage:

```bash
python -m pytest -q
```

## Scheduler and scheduled jobs

A simple scheduler process is available for scheduled background tasks, including daily summary refreshes:

```bash
python run_scheduler.py
```

You can also run the scheduler in Docker using:

```bash
docker-compose up --build scheduler
```

The old `run_worker.py` entrypoint is kept for compatibility and forwards to the scheduler.

## CI

A GitHub Actions workflow is included at `.github/workflows/ci.yml` to run tests on push and pull requests.

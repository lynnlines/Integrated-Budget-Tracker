Demo dataset and seed instructions

- Demo CSV: `data/sample_transactions.csv`
- Demo seeder: `app/db/seed_demo.py`

How to run the demo seeder (Windows PowerShell):

```powershell
.venv\Scripts\python.exe -m app.db.seed_demo
```

What it does:
- Creates a `Demo Account` if missing
- Ensures categories from the CSV exist
- Inserts transactions from `data/sample_transactions.csv` while skipping duplicates

Quick check: after running the seeder you can start the FastAPI app and call the cached summary endpoint for a month present in the CSV, e.g. June 2026:

```bash
curl "http://127.0.0.1:8000/api/v1/summary/cache/monthly?year=2026&month=6"
```

If you'd like, I can also add a tiny script that prints a ready-made curl command to inspect sample accounts and transactions.

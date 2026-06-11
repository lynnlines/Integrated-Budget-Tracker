"""Tiny CLI for common developer/demo tasks.

Usage examples:
    .venv\Scripts\python.exe -m app.cli seed-demo
    .venv\Scripts\python.exe -m app.cli show-curl --year 2026 --month 6
    .venv\Scripts\python.exe -m app.cli refresh-summary --year 2026 --month 6
"""
import os
import argparse
import json
import sys

# Default DATABASE_URL to the file DB used by alembic when not configured.
if os.getenv("DATABASE_URL") is None:
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.db.session import SessionLocal


def cmd_seed_demo(args):
    from app.db import seed_demo
    from sqlalchemy.exc import OperationalError

    try:
        seed_demo.seed()
    except OperationalError as oe:
        print("DB error:", oe)
        print("It looks like the database schema is missing. Run your migrations (e.g. `alembic upgrade head`) or create the DB before seeding.")
        raise


def cmd_show_curl(args):
    host = args.host or "http://127.0.0.1:8000"
    year = args.year
    month = args.month
    curl = f"curl \"{host}/api/v1/summary/cache/monthly?year={year}&month={month}\""
    print(curl)


def cmd_refresh_summary(args):
    from app.services.monthly_summary import refresh_monthly_summary

    db = SessionLocal()
    try:
        rec = refresh_monthly_summary(db, args.year, args.month)
        # Try to create a sensible JSON representation
        out = {}
        if rec is None:
            print("No summary returned.")
            return
        # support SQLAlchemy model or dict-like
        if hasattr(rec, "__dict__"):
            # filter private attrs
            out = {k: v for k, v in rec.__dict__.items() if not k.startswith("_")}
        elif isinstance(rec, dict):
            out = rec
        else:
            out = {"repr": repr(rec)}
        print(json.dumps(out, default=str, indent=2))
    finally:
        db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="app.cli")
    sub = parser.add_subparsers(dest="cmd")

    p_seed = sub.add_parser("seed-demo", help="Load demo CSV into DB")
    p_seed.set_defaults(func=cmd_seed_demo)

    p_curl = sub.add_parser("show-curl", help="Print curl for cached monthly summary")
    p_curl.add_argument("--year", type=int, required=True)
    p_curl.add_argument("--month", type=int, required=True)
    p_curl.add_argument("--host", required=False)
    p_curl.set_defaults(func=cmd_show_curl)

    p_refresh = sub.add_parser("refresh-summary", help="Refresh and print monthly summary via service")
    p_refresh.add_argument("--year", type=int, required=True)
    p_refresh.add_argument("--month", type=int, required=True)
    p_refresh.set_defaults(func=cmd_refresh_summary)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    try:
        args.func(args)
        return 0
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

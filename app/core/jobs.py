import logging
from datetime import datetime

from app.core.worker import ScheduledJob, Scheduler
from app.db.session import SessionLocal
from app.services.monthly_summary import refresh_current_month_summary

logger = logging.getLogger(__name__)


def heartbeat_task() -> None:
    logger.info("Worker heartbeat: scheduled tasks runner is alive")


def monthly_summary_refresh_task() -> None:
    logger.info("Running scheduled monthly summary refresh")
    with SessionLocal() as db:
        refresh_current_month_summary(db)
    logger.info("Monthly summary refresh complete")


def register_default_jobs(scheduler: Scheduler) -> None:
    scheduler.register(ScheduledJob(name="heartbeat", func=heartbeat_task, interval_seconds=3600))
    scheduler.register(ScheduledJob(name="refresh-monthly-summary", func=monthly_summary_refresh_task, interval_seconds=86400))

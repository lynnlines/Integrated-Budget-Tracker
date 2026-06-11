import threading
import time
from datetime import datetime, timedelta

from app.core.worker import ScheduledJob, Scheduler


def test_scheduled_job_should_run_on_interval():
    now = datetime.utcnow()
    job = ScheduledJob(name="test", func=lambda: None, interval_seconds=60, last_run=now - timedelta(seconds=61))

    assert job.should_run(datetime.utcnow()) is True
    job.last_run = datetime.utcnow()
    assert job.should_run(datetime.utcnow() + timedelta(seconds=30)) is False
    assert job.should_run(datetime.utcnow() + timedelta(seconds=61)) is True


def test_scheduler_executes_registered_job():
    event = threading.Event()

    def job_func() -> None:
        event.set()

    scheduler = Scheduler(tick_seconds=0.01)
    scheduler.register(ScheduledJob(name="fast-job", func=job_func, interval_seconds=0))
    scheduler.start()

    assert event.wait(1.0), "Expected scheduled job to run at least once"
    scheduler.stop()

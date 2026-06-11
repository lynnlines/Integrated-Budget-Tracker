from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    name: str
    func: Callable[[], None]
    interval_seconds: int
    last_run: Optional[datetime] = None
    enabled: bool = True

    def should_run(self, now: datetime) -> bool:
        if not self.enabled:
            return False
        if self.last_run is None:
            return True
        return (now - self.last_run).total_seconds() >= self.interval_seconds

    def run(self) -> None:
        logger.debug("Starting scheduled job %s", self.name)
        self.func()
        self.last_run = datetime.utcnow()
        logger.debug("Finished scheduled job %s", self.name)


class Scheduler:
    def __init__(self, tick_seconds: int = 60) -> None:
        self.tick_seconds = max(1, tick_seconds)
        self.jobs: list[ScheduledJob] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def register(self, job: ScheduledJob) -> None:
        self.jobs.append(job)
        logger.info("Registered scheduled job %s", job.name)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="SchedulerThread")
        self._thread.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            now = datetime.utcnow()
            for job in list(self.jobs):
                if job.should_run(now):
                    try:
                        job.run()
                    except Exception:
                        logger.exception("Scheduled job failure: %s", job.name)
            self._stop_event.wait(self.tick_seconds)

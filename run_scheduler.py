import logging
import time

from app.core.jobs import register_default_jobs
from app.core.worker import Scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    scheduler = Scheduler(tick_seconds=30)
    register_default_jobs(scheduler)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler shutdown requested")
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()

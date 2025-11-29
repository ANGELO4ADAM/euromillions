import logging
from typing import Any, Dict

try:
    from celery import Celery
except ImportError:  # pragma: no cover - optional dependency
    class Celery:  # type: ignore
        def __init__(self, *_, **__):
            self.tasks = {}

        def task(self, *_, **__):
            def decorator(func):
                self.tasks[func.__name__] = func
                return func

            return decorator

        def send_task(self, name: str, args=None, kwargs=None):
            func = self.tasks.get(name)
            if func:
                return func(*(args or ()), **(kwargs or {}))
            raise RuntimeError(f"Task {name} not found")


celery_app = Celery("eop", broker="redis://localhost:6379/0")
logger = logging.getLogger(__name__)

# Minimal logger configuration to surface worker activity in development environments
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


@celery_app.task
def import_csv_task(path: str) -> Dict[str, Any]:
    logger.info("Importing CSV from %s", path)
    return {"status": "imported", "path": path}


@celery_app.task
def entrainer_ia() -> Dict[str, str]:
    logger.info("Training IA")
    return {"status": "trained"}


@celery_app.task
def entrainer_intensif() -> Dict[str, str]:
    logger.info("Intensive training")
    return {"status": "intensive_trained"}


@celery_app.task
def debriefing() -> Dict[str, str]:
    return {"status": "debriefing_ready"}


@celery_app.task
def debriefing_flash() -> Dict[str, str]:
    return {"status": "flash_ready"}


@celery_app.task
def tache_sonar() -> Dict[str, str]:
    return {"status": "sonar_complete"}


@celery_app.task
def ghost_prediction() -> Dict[str, str]:
    return {"status": "ghost_predictions_generated"}


@celery_app.task
def launch_campaign(name: str) -> Dict[str, str]:
    return {"status": "campaign_launched", "name": name}


@celery_app.task
def maintenance() -> Dict[str, str]:
    return {"status": "maintenance_done"}


@celery_app.task
def cleanup() -> Dict[str, str]:
    return {"status": "cleanup_done"}

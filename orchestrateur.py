from typing import Dict

from tasks import (
    cleanup,
    debriefing,
    debriefing_flash,
    entrainer_ia,
    entrainer_intensif,
    ghost_prediction,
    import_csv_task,
    launch_campaign,
    maintenance,
    tache_sonar,
)


class Orchestrateur:
    """Facade to trigger asynchronous jobs for the platform."""

    def lancer_import(self, path: str) -> Dict[str, str]:
        return import_csv_task(path)

    def lancer_training(self) -> Dict[str, str]:
        return entrainer_ia()

    def lancer_training_intensif(self) -> Dict[str, str]:
        return entrainer_intensif()

    def lancer_debriefing(self) -> Dict[str, str]:
        return debriefing()

    def lancer_debriefing_flash(self) -> Dict[str, str]:
        return debriefing_flash()

    def lancer_sonar(self) -> Dict[str, str]:
        return tache_sonar()

    def lancer_ghost(self) -> Dict[str, str]:
        return ghost_prediction()

    def lancer_campagne(self, name: str) -> Dict[str, str]:
        return launch_campaign(name)

    def lancer_maintenance(self) -> Dict[str, str]:
        return maintenance()

    def lancer_cleanup(self) -> Dict[str, str]:
        return cleanup()

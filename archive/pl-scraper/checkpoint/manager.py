import json
import signal
from pathlib import Path
from datetime import datetime
from loguru import logger

# Estructura base del checkpoint
DEFAULT_STATE = {
    "version": 1,
    "last_updated": None,
    "seasons": {}
}

class CheckpointManager:
    def __init__(self, season=None):
        self.season = season
        self.filename = Path(f"checkpoint_{season}.json") if season else Path("checkpoint.json")
        self.state = self._load()
        self._stop_requested = False
        # Captura Ctrl+C para pausar limpiamente
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _handle_sigint(self, sig, frame):
        logger.warning("⏸  Ctrl+C detectado — finalizando tarea actual y guardando checkpoint...")
        self._stop_requested = True

    def _load(self):
        if self.filename.exists():
            with open(self.filename) as f:
                data = json.load(f)
            logger.info(f"📂 Checkpoint cargado [{self.filename}] — último update: {data.get('last_updated')}")
            return data
        logger.info(f"🆕 No hay checkpoint previo [{self.filename}], iniciando desde cero")
        return DEFAULT_STATE.copy()

    def save(self):
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.filename, "w") as f:
            json.dump(self.state, f, indent=2)

    def should_stop(self) -> bool:
        return self._stop_requested

    # --- Helpers de estado por season ---

    def init_season(self, season: int):
        key = str(season)
        if key not in self.state["seasons"]:
            self.state["seasons"][key] = {
                "status": "pending",
                "schedule_done": False,
                "lineups_done": False,
                "events_done": False,
                "shots_done": False,
                "player_stats_done": [],
                "match_ids_total": [],
                "match_ids_done": {
                    "lineups": [], "events": [], "shots": [],
                    "summary": [], "shooting": [], "passing": [],
                    "defense": [], "possession": [], "misc": [], "keeper": []
                },
                "started_at": datetime.now().isoformat(),
                "finished_at": None
            }
            self.save()

    def is_season_done(self, season: int) -> bool:
        return self.state["seasons"].get(str(season), {}).get("status") == "done"

    def mark_schedule_done(self, season: int, match_ids: list):
        s = self.state["seasons"][str(season)]
        s["schedule_done"] = True
        s["match_ids_total"] = match_ids
        s["status"] = "in_progress"
        self.save()

    def is_match_done(self, season: int, task: str, match_id: str) -> bool:
        done_list = self.state["seasons"][str(season)]["match_ids_done"].get(task, [])
        return match_id in done_list

    def mark_match_done(self, season: int, task: str, match_id: str):
        self.state["seasons"][str(season)]["match_ids_done"][task].append(match_id)
        self.save()

    def mark_season_done(self, season: int):
        s = self.state["seasons"][str(season)]
        s["status"] = "done"
        s["finished_at"] = datetime.now().isoformat()
        self.save()

    def get_pending_matches(self, season: int, task: str) -> list:
        s = self.state["seasons"][str(season)]
        total = s["match_ids_total"]
        done  = s["match_ids_done"].get(task, [])
        return [m for m in total if m not in done]

    def progress_summary(self) -> dict:
        """Retorna resumen para el dashboard"""
        summary = {}
        for season, data in self.state["seasons"].items():
            total = len(data["match_ids_total"])
            done_lineups = len(data["match_ids_done"]["lineups"])
            done_events  = len(data["match_ids_done"]["events"])
            done_shots   = len(data["match_ids_done"]["shots"])
            summary[season] = {
                "status": data["status"],
                "total_matches": total,
                "lineups":  f"{done_lineups}/{total}",
                "events":   f"{done_events}/{total}",
                "shots":    f"{done_shots}/{total}",
                "player_stats": data["player_stats_done"]
            }
        return summary

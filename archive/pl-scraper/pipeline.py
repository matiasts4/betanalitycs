import time
from loguru import logger
from config import SEASONS_TODO, STAT_TYPES, RATE_LIMIT_SECONDS
from scraper.fbref_client import get_fbref
from storage.db import upsert_matches, upsert_lineups, upsert_events, upsert_shots, upsert_player_stats
from checkpoint.manager import CheckpointManager

def run_season(season, browser_client=None):
    """Ejecuta el pipeline completo para una sola temporada."""
    # Configurar log específico para esta temporada
    log_file = f"logs/scraper_{season}.log"
    logger.add(log_file, rotation="10 MB", level="INFO", filter=lambda record: record["extra"].get("season") == str(season))
    s_logger = logger.bind(season=str(season))
    
    cp = CheckpointManager(season=season)

    # Saltar temporadas ya completadas
    if cp.is_season_done(season):
        logger.info(f"⏭  Temporada {season} ya completa, saltando")
        return

    try:
        s_num = int(season)
        s_display = f"{s_num}/{str(s_num+1)[-2:]}"
    except:
        s_display = str(season)
        
    logger.info(f"⏳ Iniciando temporada {s_display}")
    cp.init_season(season)
    
    # Obtener cliente de FBRef con el navegador inyectado
    fbref = get_fbref(season, browser_client=browser_client)

    # ── FASE 1: Schedule ──────────────────────────────────────────
    if not cp.state["seasons"][str(season)]["schedule_done"]:
        schedule = fbref.read_schedule()
        upsert_matches(schedule, season)
        if 'game_id' in schedule.columns:
            match_ids = schedule['game_id'].dropna().unique().tolist()
        elif 'game_id' in schedule.index.names:
            match_ids = schedule.index.get_level_values('game_id').unique().tolist()
        else:
            match_ids = schedule.index.tolist()
        cp.mark_schedule_done(season, [str(m) for m in match_ids])
        logger.success(f"  ✅ Schedule: {len(match_ids)} partidos")
        time.sleep(RATE_LIMIT_SECONDS)
    else:
        logger.info(f"  ⏭  Schedule ya scrapeado")

    # ── FASE 2: Procesamiento unificado por Partido ────────────────
    pending_lineups = set(cp.get_pending_matches(season, "lineups"))
    pending_events = set(cp.get_pending_matches(season, "events"))
    pending_shots = set(cp.get_pending_matches(season, "shots"))
    
    all_pending_matches = pending_lineups | pending_events | pending_shots
    
    if all_pending_matches:
        logger.info(f"  🔄 Datos pendientes para {len(all_pending_matches)} partidos")
        # Ordenamos los IDs para consistencia
        for match_id in sorted(list(all_pending_matches)):
            if cp.should_stop(): return _pause()
            
            logger.info(f"  ⚽ Extrayendo datos del partido: {match_id}")
            
            # Alineaciones
            if match_id in pending_lineups:
                try:
                    df = fbref.read_lineup(match_id=[match_id])
                    upsert_lineups(df, season)
                    cp.mark_match_done(season, "lineups", match_id)
                except Exception as e:
                    logger.warning(f"    ⚠️  Lineup {match_id}: {e}")
            
            # Eventos
            if match_id in pending_events:
                try:
                    df = fbref.read_events(match_id=[match_id])
                    upsert_events(df, season)
                    cp.mark_match_done(season, "events", match_id)
                except Exception as e:
                    logger.warning(f"    ⚠️  Event {match_id}: {e}")
            
            # Tiros
            if match_id in pending_shots:
                try:
                    df = fbref.read_shot_events(match_id=[match_id])
                    upsert_shots(df, season)
                    cp.mark_match_done(season, "shots", match_id)
                except Exception as e:
                    logger.warning(f"    ⚠️  Shot {match_id}: {e}")
                    
            # Pausa para este partido completo (el navegador cargará solo 1 vez la página HTML)
            time.sleep(RATE_LIMIT_SECONDS)
    else:
        logger.info("  ⏭  Alineaciones, Eventos y Tiros completados para esta temporada")

    # ── FASE 3: Player match stats ────────────────────────────────
    stats_done = cp.state["seasons"][str(season)]["player_stats_done"]
    for stat in STAT_TYPES:
        if stat in stats_done:
            continue
        if cp.should_stop(): return _pause()
        try:
            df = fbref.read_player_match_stats(stat_type=stat)
            upsert_player_stats(df, season, stat)
            cp.state["seasons"][str(season)]["player_stats_done"].append(stat)
            cp.save()
            logger.success(f"  ✅ player_stats [{stat}]")
        except Exception as e:
            logger.warning(f"  ⚠️  player_stats [{stat}]: {e}")
            if "Invalid argument: stat_type should be in" in str(e):
                logger.info(f"  📌  Marking [{stat}] as complete (not available for season {season})")
                cp.state["seasons"][str(season)]["player_stats_done"].append(stat)
                cp.save()
        time.sleep(RATE_LIMIT_SECONDS)

    cp.mark_season_done(season)
    s_logger.success(f"✅ Temporada {season} completada")

def run(seasons=SEASONS_TODO):
    # Ensure logs directory exists
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)

    for season in seasons:
        run_season(season)

def _pause():
    logger.warning("⏸  Pipeline pausado. Checkpoint guardado. Ejecuta `python pipeline.py` para reanudar.")

if __name__ == "__main__":
    run()

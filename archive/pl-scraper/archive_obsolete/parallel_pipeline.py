import multiprocessing
import time
from loguru import logger
from config import SEASONS_TODO
from pipeline import run_season
from scraper.browser_client import BrowserClient

def season_worker(season, proxy=None, headless=True):
    """
    Worker que maneja una sola temporada en su propio proceso.
    """
    logger.info(f"🚀 Iniciando worker paralelo para temporada {season}")
    client = None
    try:
        # Cada proceso crea su propia instancia de navegador
        client = BrowserClient(proxy=proxy, headless=headless)
        
        # Ejecuta la lógica del pipeline para esta temporada
        run_season(season, browser_client=client)
        
        logger.success(f"✨ Worker para temporada {season} finalizó exitosamente")
    except Exception as e:
        logger.error(f"❌ Error crítico en worker de temporada {season}: {e}")
    finally:
        if client:
            client.close()

def run_parallel(seasons=SEASONS_TODO, max_workers=2, proxies=None):
    """
    Lanza el scraping en paralelo para las temporadas especificadas.
    :param seasons: Lista de temporadas.
    :param max_workers: Número máximo de procesos simultáneos.
    :param proxies: Lista opcional de proxies (uno por season o rotativos).
    """
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    
    logger.info(f"🔥 Iniciando scraping paralelo con {max_workers} workers para {len(seasons)} temporadas")
    
    processes = []
    
    # Para simplificar, dividimos las temporadas en grupos según max_workers
    # o simplemente usamos un Pool. Usaremos Process directos para mayor control de recursos.
    
    # Nota: Si no hay proxies, recomendamos max_workers bajo (ej. 2)
    
    for i, season in enumerate(seasons):
        proxy = proxies[i % len(proxies)] if proxies else None
        
        p = multiprocessing.Process(
            target=season_worker,
            args=(season, proxy, True), # Headless True para paralelo
            name=f"Scraper-{season}"
        )
        p.start()
        processes.append(p)
        
        # Pequeño delay entre inicios de procesos para no saturar CPU/Red de una vez
        time.sleep(10)
        
        # Limitar número de trabajadores activos simultáneamente
        while len([pr for pr in processes if pr.is_alive()]) >= max_workers:
            time.sleep(5)

    # Esperar a que todos terminen
    for p in processes:
        p.join()

    logger.success("🏁 Scraping paralelo completado.")

if __name__ == "__main__":
    # Ejemplo de uso: 2 seasons en paralelo por defecto (para cuidar la IP si no hay proxies)
    # Si tienes proxies, puedes subir max_workers a 4 o 5.
    import sys
    
    target_seasons = SEASONS_TODO
    if len(sys.argv) > 1:
        target_seasons = sys.argv[1:]
        
    run_parallel(seasons=target_seasons, max_workers=2)

import multiprocessing
import time
from scraper.browser_client import BrowserClient

def test_worker(id):
    print(f"Buscando navegador en worker {id}...")
    client = BrowserClient(headless=True)
    try:
        # Solo navegar a la home para probar conectividad y CF bypass
        html = client.get_html("https://fbref.com")
        print(f"Worker {id} obtuvo HTML de {len(html)} bytes")
    finally:
        client.close()
        print(f"Worker {id} cerrado.")

if __name__ == "__main__":
    print("Iniciando prueba paralela de 2 instancias...")
    p1 = multiprocessing.Process(target=test_worker, args=(1,))
    p2 = multiprocessing.Process(target=test_worker, args=(2,))
    
    p1.start()
    time.sleep(5) # Delay para no abrir ambas a la vez
    p2.start()
    
    p1.join()
    p2.join()
    print("Prueba completada.")

import time
from seleniumbase import Driver
from loguru import logger

class BrowserClient:
    def __init__(self, proxy=None, headless=False):
        """
        Initializes a new SeleniumBase browser session.
        :param proxy: Optional proxy string (e.g., "username:password@host:port")
        :param headless: Whether to run in headless mode.
        """
        self.driver = None
        self.proxy = proxy
        self.headless = headless
        self._init_driver()

    def _init_driver(self):
        """Starts the browser with SeleniumBase (Anti-Detect)."""
        logger.info(f"Iniciando navegador con SeleniumBase (Anti-Detect)... {'[Proxy: ' + self.proxy + ']' if self.proxy else ''}")
        
        # SeleniumBase Driver with undetected-chromedriver mode (uc=True)
        self.driver = Driver(uc=True, headless=self.headless, proxy=self.proxy)
        
        logger.info("Navegando a FBref para establecer la sesión...")
        self.driver.get("https://fbref.com")
        
        # Wait for Cloudflare challenge to pass
        if not self._wait_for_cloudflare():
            logger.error("No se pudo superar el desafío de Cloudflare al inicio.")

    def _wait_for_cloudflare(self, timeout=120):
        """Waits until the Cloudflare 'Just a moment...' text disappears."""
        logger.info("Detectando si hay desafío de Cloudflare...")
        time.sleep(2)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            title = self.driver.title.lower()
            page_src = self.driver.page_source.lower()
            
            if "just a moment" not in title and "cloudflare" not in title and "enable javascript" not in page_src and "challenge" not in title:
                logger.success("Cloudflare limpio. Procediendo con el scraping.")
                return True
                
            logger.warning("Desafío de Cloudflare activo. Por favor resuélvelo manualmente en la ventana si solicita hacer clic...")
            time.sleep(5)
            
        logger.error("Se agotó el tiempo esperando resolver Cloudflare (2 min).")
        return False

    def get_html(self, url: str, max_retries: int = 3) -> bytes:
        """
        Given a URL, loads it through this browser instance,
        waits for it to render, and returns the raw HTML source code as bytes.
        """
        for attempt in range(max_retries):
            try:
                logger.debug(f"Página: {url}")
                self.driver.get(url)
                
                self._wait_for_cloudflare(timeout=120)
                
                # Wait a bit for JS to render stats tables fully
                time.sleep(3) 
                
                html_content = self.driver.page_source
                return html_content.encode("utf-8")
                
            except Exception as e:
                logger.warning(f"Error cargando {url} (Intento {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise ConnectionError(f"No se pudo cargar la URL después de {max_retries} intentos: {url}")

    def close(self):
        """Properly close the browser instance."""
        if self.driver:
            self.driver.quit()
            self.driver = None


# Legacy support or quick helper if needed (singleton-like for simple scripts)
_global_client = None

def get_html_with_browser(url: str, max_retries: int = 3) -> bytes:
    global _global_client
    if _global_client is None:
        _global_client = BrowserClient()
    return _global_client.get_html(url, max_retries)

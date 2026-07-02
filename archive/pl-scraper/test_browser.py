from scraper.browser_client import get_html_with_browser
from loguru import logger

def test():
    logger.info("Initializing browser test to fbref.com to test Cloudflare bypass...")
    try:
        html = get_html_with_browser("https://fbref.com/en/comps/9/Premier-League-Stats")
        logger.success(f"Successfully retrieved HTML. Length: {len(html)} bytes")
        
        from scraper.browser_client import BrowserClient
        BrowserClient.close()
    except Exception as e:
        logger.error(f"Failed to fetch page: {e}")

if __name__ == "__main__":
    test()

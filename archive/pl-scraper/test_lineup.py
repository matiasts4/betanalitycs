import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from scraper.browser_client import BrowserClient
from scraper.fbref_client import get_fbref

browser = BrowserClient(headless=False)
fbref = get_fbref("2025", browser_client=browser)

try:
    print("Reading lineup for 02dbe729...")
    df = fbref.read_lineup(match_id=["02dbe729"])
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
finally:
    browser.close()

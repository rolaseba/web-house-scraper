"""
Web scraper module for extracting property data from Argenprop and Zonaprop.
Uses multiple strategies to bypass anti-scraping measures.
"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyScraper:
    """Scraper for real estate websites with anti-bot bypass capabilities."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    
    def fetch_with_requests(self, url):
        """Try to fetch URL using requests with browser headers."""
        try:
            logger.info(f"Fetching with requests: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Requests failed for {url}: {e}")
            return None
    
    def fetch_with_playwright(self, url):
        """Fetch URL using Playwright (headless browser)."""
        try:
            logger.info(f"Fetching with Playwright: {url}")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    locale='es-AR',
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
                        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
                    }
                )
                page = context.new_page()
                
                # Use 'load' instead of 'networkidle' to avoid timeout issues
                page.goto(url, wait_until='load', timeout=60000)
                
                # Wait for content to load (adjust selector based on site)
                time.sleep(3)  # Simple wait to ensure dynamic content loads
                
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Playwright failed for {url}: {e}")
            return None
    
    def fetch_html(self, url):
        """
        Fetch HTML content from a URL using the best available method.
        First tries requests, falls back to Playwright if needed.
        """
        # Try requests first (faster)
        html = self.fetch_with_requests(url)
        
        # Check if content is valid (some sites return empty/short body when blocking)
        if html and len(html) < 1000:
            logger.warning(f"Fetched content too short ({len(html)} chars). Treating as failure.")
            html = None
        
        # Fallback to Playwright if requests failed or content was invalid
        if not html:
            logger.info("Falling back to Playwright...")
            html = self.fetch_with_playwright(url)
        
        if not html:
            raise Exception(f"Failed to fetch content from {url}")
        
        return html
    
    def extract_text_content(self, html):
        """
        Extract meaningful text from HTML while removing scripts, styles, etc.
        This reduces noise for the LLM processing.
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)
        
        return text
    
    def scrape_property(self, url):
        """
        Main method to scrape a property listing.
        Returns raw HTML and cleaned text for LLM processing.
        """
        logger.info(f"Scraping property: {url}")
        
        html = self.fetch_html(url)
        text = self.extract_text_content(html)
        
        return {
            'url': url,
            'html': html,
            'text': text[:50000],  # Limit text size to avoid excessive LLM tokens
        }


def test_scraper():
    """Test function to verify scraper works."""
    scraper = PropertyScraper()
    
    test_urls = [
        "https://www.zonaprop.com.ar/propiedades/clasificado/veclphin-casa-de-pasillo-reciclada-de-3-dorm.-con-patio-y-56598216.html",
        "https://www.argenprop.com/departamento-en-venta-en-centro-6-ambientes--18157682",
    ]
    
    for url in test_urls:
        try:
            result = scraper.scrape_property(url)
            print(f"\n{'='*80}")
            print(f"URL: {result['url']}")
            print(f"Text length: {len(result['text'])} characters")
            print(f"Preview: {result['text'][:500]}...")
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"Error scraping {url}: {e}")


if __name__ == "__main__":
    test_scraper()

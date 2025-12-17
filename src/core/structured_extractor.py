"""
Structured data extractor using site-specific configurations.
Extracts data using CSS selectors and regex patterns before LLM processing.
"""

import re
import json
import logging
import os
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.utils import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StructuredExtractor:
    """Extract structured data from HTML using site-specific patterns."""
    
    def __init__(self, config_file: str = None):
        """Load site configurations."""
        if config_file is None:
            # Default path: data/site_configs.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_file = os.path.join(base_dir, "data", "site_configs.json")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            self.configs = json.load(f)
        logger.info(f"Loaded configurations for {len([k for k in self.configs if not k.startswith('_')])} sites")
    
    def get_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    
    def get_config(self, url: str) -> Optional[Dict]:
        """Get configuration for a URL's domain."""
        domain = self.get_domain(url)
        return self.configs.get(domain)
    
    def extract_with_regex(self, pattern: str, text: str, transform: Dict = None) -> Optional[str]:
        """Extract data using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            
            # Apply transformation if defined
            if transform and value in transform:
                value = transform[value]
            
            return value
        return None
    
    def extract_with_css(self, soup: BeautifulSoup, selector: str, regex: str = None, transform: Dict = None) -> Optional[str]:
        """Extract data using CSS selector, optionally with regex."""
        element = soup.select_one(selector)
        if not element:
            return None
        
        text = element.get_text(strip=True)
        
        if regex:
            return self.extract_with_regex(regex, text, transform)
        
        if transform and text in transform:
            return transform[text]
        
        return text
    
    def extract_field(self, field_name: str, field_config: Dict, html: str, text: str) -> Optional[Any]:
        """Extract a single field using its configuration."""
        pattern_type = field_config.get('type')
        
        # Skip LLM-required fields
        if pattern_type == 'llm_required':
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        if pattern_type == 'regex':
            pattern = field_config['pattern']
            search_in = field_config.get('search_in', 'text')
            transform = field_config.get('transform')
            
            content = html if search_in == 'html' else text
            value = self.extract_with_regex(pattern, content, transform)
            
            # Try to convert to appropriate type
            if value:
                if field_name in ['metros_cuadrados_cubiertos', 'metros_cuadrados_totales', 
                                'cantidad_dormitorios', 'cantidad_banos', 'precio']:
                    try:
                        # Remove commas and convert to number
                        value = value.replace(',', '').replace('.', '')
                        value = int(value)
                    except ValueError:
                        pass
                
                elif field_name in ['tiene_cochera', 'tiene_patio', 'tiene_quincho', 'tiene_pileta', 'tiene_balcon', 'tiene_terraza']:
                    try:
                        # Convert to boolean based on numeric value
                        num_value = int(value)
                        value = num_value > 0
                    except ValueError:
                        # If not a number, assume True if text is present and not "0" or "no"
                        lower_val = value.lower()
                        value = lower_val not in ["0", "no", "false", "none"]
            
            return value
        
        elif pattern_type == 'css_selector':
            selector = field_config['selector']
            regex = field_config.get('regex')
            transform = field_config.get('transform')
            
            value = self.extract_with_css(soup, selector, regex, transform)
            
            # Try to convert to number if needed
            if value:
                if field_name in ['metros_cuadrados_cubiertos', 'metros_cuadrados_totales', 
                                'cantidad_dormitorios', 'cantidad_banos', 'precio']:
                    try:
                        value = value.replace(',', '').replace('.', '')
                        value = int(value)
                    except ValueError:
                        pass
                elif field_name in ['tiene_cochera', 'tiene_patio', 'tiene_quincho', 'tiene_pileta', 'tiene_balcon', 'tiene_terraza']:
                    try:
                        num_value = int(value)
                        value = num_value > 0
                    except ValueError:
                        lower_val = value.lower()
                        value = lower_val not in ["0", "no", "false", "none"]
            
            return value
        
        return None
    
    def extract_structured_data(self, url: str, html: str, text: str) -> Dict[str, Any]:
        """
        Extract all possible structured data from HTML.
        Returns dict with extracted fields and list of fields requiring LLM.
        """
        config = self.get_config(url)
        
        if not config:
            logger.warning(f"No configuration found for URL: {url}")
            return {
                'extracted': {},
                'llm_required_fields': []
            }
        
        site_name = config.get('name', 'Unknown')
        logger.info(f"Extracting structured data for {site_name}")
        
        extracted = {}
        llm_required = []
        
        patterns = config.get('patterns', {})
        
        for field_name, field_config in patterns.items():
            if field_config.get('type') == 'llm_required':
                llm_required.append(field_name)
            else:
                value = self.extract_field(field_name, field_config, html, text)
                if value is not None:
                    extracted[field_name] = value
                    logger.info(f"  ✓ {field_name}: {value}")
                else:
                    logger.debug(f"  ✗ {field_name}: not found")
        
        return {
            'extracted': extracted,
            'llm_required_fields': llm_required
        }


def test_extractor():
    """Test the structured extractor."""
    from scraper import PropertyScraper
    
    scraper = PropertyScraper()
    extractor = StructuredExtractor()
    
    # Test Zonaprop
    url1 = "https://www.zonaprop.com.ar/propiedades/clasificado/veclphin-casa-de-pasillo-reciclada-de-3-dorm.-con-patio-y-56598216.html"
    result1 = scraper.scrape_property(url1)
    data1 = extractor.extract_structured_data(url1, result1['html'], result1['text'])
    
    print("\n" + "="*80)
    print("ZONAPROP EXTRACTION")
    print("="*80)
    print(json.dumps(data1, indent=2, ensure_ascii=False))
    
    # Test Argenprop
    url2 = "https://www.argenprop.com/departamento-en-venta-en-centro-6-ambientes--18157682"
    result2 = scraper.scrape_property(url2)
    data2 = extractor.extract_structured_data(url2, result2['html'], result2['text'])
    
    print("\n" + "="*80)
    print("ARGENPROP EXTRACTION")
    print("="*80)
    print(json.dumps(data2, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_extractor()

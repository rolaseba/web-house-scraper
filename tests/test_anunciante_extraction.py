import sys
import os
from bs4 import BeautifulSoup

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.structured_extractor import StructuredExtractor

def test_anunciante_extraction():
    extractor = StructuredExtractor()
    
    # Test cases
    test_cases = [
        {
            "site": "zonaprop.com.ar",
            "url": "https://www.zonaprop.com.ar/propiedades/test.html",
            "html": '<h3 class="publisherData-module__publisher-name___6HD5R publisherData-module__property___1tpXW" data-qa="linkMicrositioAnunciante">Sergio Villella Bienes Inmuebles</h3>',
            "expected": "Sergio Villella Bienes Inmuebles"
        },
        {
            "site": "argenprop.com",
            "url": "https://www.argenprop.com/casa-en-venta.html",
            "html": '<p class="form-details-heading">MA Propiedades</p>',
            "expected": "MA Propiedades"
        },
        {
            "site": "mercadolibre.com.ar",
            "url": "https://departamento.mercadolibre.com.ar/MLA-1582084609-test.html",
            "html": '<div id="seller_profile"><div class="ui-vip-profile-info"><div class="ui-vip-profile-info__info-container"><div><h3><span>Vanzini Propiedades</span></h3></div></div></div></div>',
            "expected": "Vanzini Propiedades"
        }
    ]
    
    passed = 0
    for case in test_cases:
        print(f"Testing {case['site']}...")
        result = extractor.extract_structured_data(case['url'], case['html'], "")
        extracted = result['extracted'].get('anunciante')
        
        if extracted == case['expected']:
            print(f"  ✓ SUCCESS: Extracted '{extracted}'")
            passed += 1
        else:
            print(f"  ✗ FAILED: Expected '{case['expected']}', got '{extracted}'")
            
    print(f"\nResults: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

if __name__ == "__main__":
    test_anunciante_extraction()

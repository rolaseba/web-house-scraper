"""
Test script to verify square meters extraction as REAL with 2 decimal places.
Tests the structured extractor with sample data.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.structured_extractor import StructuredExtractor


def test_square_meters_extraction():
    """Test that square meters are extracted as REAL with 2 decimals."""
    
    extractor = StructuredExtractor()
    
    # Test cases: (input_value, expected_output)
    test_cases = [
        ("72.5", 72.5),
        ("72,5", 72.5),
        ("100", 100.0),
        ("85.75", 85.75),
        ("120.123", 120.12),  # Should round to 2 decimals
        ("50,99", 50.99),
    ]
    
    print("Testing _standardize_square_meters function:")
    print("=" * 60)
    
    all_passed = True
    for input_val, expected in test_cases:
        try:
            result = extractor._standardize_square_meters(input_val)
            passed = result == expected
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: Input: {input_val:10s} → Output: {result:6.2f} (Expected: {expected:6.2f})")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"✗ ERROR: Input: {input_val:10s} → Exception: {e}")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    
    return all_passed


def test_field_extraction():
    """Test extraction from sample HTML/text."""
    
    extractor = StructuredExtractor()
    
    print("\nTesting field extraction from sample data:")
    print("=" * 60)
    
    # Sample Zonaprop-like HTML
    sample_html = """
    <div class="property">
        <span>72.5 m² cub.</span>
        <span>100 m² tot.</span>
        <span>3 dorm</span>
        <span>2 baño</span>
    </div>
    """
    
    sample_text = "72.5 m² cub. 100 m² tot. 3 dorm 2 baño"
    
    # Test Zonaprop config
    url = "https://www.zonaprop.com.ar/test-property"
    result = extractor.extract_structured_data(url, sample_html, sample_text)
    
    print(f"Extracted data from Zonaprop-like content:")
    for field, value in result['extracted'].items():
        print(f"  {field}: {value} (type: {type(value).__name__})")
    
    # Verify types
    if 'metros_cuadrados_cubiertos' in result['extracted']:
        m2_cub = result['extracted']['metros_cuadrados_cubiertos']
        if isinstance(m2_cub, float) and m2_cub == 72.5:
            print("✓ metros_cuadrados_cubiertos is REAL with correct value")
        else:
            print(f"✗ metros_cuadrados_cubiertos failed: {m2_cub} (type: {type(m2_cub)})")
    
    if 'metros_cuadrados_totales' in result['extracted']:
        m2_tot = result['extracted']['metros_cuadrados_totales']
        if isinstance(m2_tot, float) and m2_tot == 100.0:
            print("✓ metros_cuadrados_totales is REAL with correct value")
        else:
            print(f"✗ metros_cuadrados_totales failed: {m2_tot} (type: {type(m2_tot)})")
    
    print("=" * 60)


if __name__ == "__main__":
    print("Square Meters REAL Type Conversion - Test Suite")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_square_meters_extraction()
    test_field_extraction()
    
    print("\nTest suite completed!")
    sys.exit(0 if test1_passed else 1)

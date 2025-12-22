"""
Test script for the value standardization layer.
"""

from src.core.input_transformation import standardize_data
from rich.console import Console
from rich.table import Table

console = Console()

def test_standardization():
    test_cases = [
        # Address tests
        {
            "name": "Full address cleaning",
            "input": {"direccion": "3 De Febrero 1208 '09-01, Centro, Rosario"},
            "expected": {"direccion": "3 De Febrero 1208"}
        },
        {
            "name": "Address with 'al'",
            "input": {"direccion": "Moreno  al 400"},
            "expected": {"direccion": "Moreno 400"}
        },
        # Antiquity tests
        {
            "name": "Antiquity 'a estrenar'",
            "input": {"antiguedad": "a estrenar"},
            "expected": {"antiguedad": 0}
        },
        {
            "name": "Antiquity '0 años'",
            "input": {"antiguedad": "0 años"},
            "expected": {"antiguedad": 0}
        },
        {
            "name": "Antiquity '15 años'",
            "input": {"antiguedad": "15 años"},
            "expected": {"antiguedad": 15}
        },
        # Numeric tests
        {
            "name": "Price with symbols",
            "input": {"precio": "USD 180.000"},
            "expected": {"precio": 180000.0}
        },
        {
            "name": "M2 with symbols",
            "input": {"metros_cuadrados_cubiertos": "120,50 m2"},
            "expected": {"metros_cuadrados_cubiertos": 120.5}
        },
        # Boolean tests
        {
            "name": "Boolean 'Sí'",
            "input": {"tiene_patio": "Sí"},
            "expected": {"tiene_patio": True}
        },
        # Piso tests
        {
            "name": "Piso 'Ninguno' to null",
            "input": {"piso": "Ninguno"},
            "expected": {"piso": None}
        },
        {
            "name": "Piso 'Planta Baja' to PB",
            "input": {"piso": "Planta Baja"},
            "expected": {"piso": "PB"}
        },
        # Numeric type tests
        {
            "name": "Integer price to float",
            "input": {"precio": 180000},
            "expected": {"precio": 180000.0}
        },
        # Calculated field exclusion test
        {
            "name": "Calculated field ignored",
            "input": {"costo_metro_cuadrado": 1500.50},
            "expected": {"costo_metro_cuadrado": 1500.50}
        }
    ]

    table = Table(title="Standardization Test Results")
    table.add_column("Test Name", style="cyan")
    table.add_column("Input", style="magenta")
    table.add_column("Expected", style="green")
    table.add_column("Actual", style="yellow")
    table.add_column("Status", justify="center")

    passed_count = 0
    
    for case in test_cases:
        actual = standardize_data(case["input"])
        
        # Check only the fields present in input/expected
        all_passed = True
        for key, expected_val in case["expected"].items():
            if actual.get(key) != expected_val:
                all_passed = False
                break
        
        status = "[green]PASS[/green]" if all_passed else "[red]FAIL[/red]"
        if all_passed:
            passed_count += 1
            
        table.add_row(
            case["name"],
            str(case["input"]),
            str(case["expected"]),
            str({k: actual.get(k) for k in case["expected"].keys()}),
            status
        )

    console.print(table)
    console.print(f"\n[bold]Results: {passed_count}/{len(test_cases)} passed[/bold]")

if __name__ == "__main__":
    test_standardization()

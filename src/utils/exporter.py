"""
Utilities for exporting database content.
"""
import csv
import logging
from typing import Optional
from rich.console import Console
from src.database.database import PropertyDatabase

logger = logging.getLogger(__name__)
console = Console()

def export_to_csv(output_path: str):
    """
    Export all properties from the database to a CSV file.
    
    Args:
        output_path: Path to the output CSV file.
    """
    try:
        with PropertyDatabase() as db:
            properties = db.get_all_properties()
            
            if not properties:
                console.print("[yellow]⚠[/yellow] No properties found in database to export.")
                return
            
            # Get headers from the first property keys
            headers = list(properties[0].keys())
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(properties)
                
            console.print(f"[green]✓[/green] Successfully exported {len(properties)} properties to [bold]{output_path}[/bold]")
            logger.info(f"Exported {len(properties)} properties to {output_path}")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to export data: {e}")
        logger.error(f"Export failed: {e}")

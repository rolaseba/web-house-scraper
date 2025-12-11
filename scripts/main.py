#!/usr/bin/env python3
"""
Main application to scrape property listings and save to database.
Reads URLs from links-to-scrap.md, scrapes using Playwright/requests,
processes with LLM, and stores in SQLite.
"""

import sys
import os
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.logging import RichHandler

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.scraper import PropertyScraper
from src.core.llm_processor import LLMProcessor
from src.database.database import PropertyDatabase
from src.utils import config

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[RichHandler(rich_tracebacks=True, show_time=False, show_path=False)]
)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()


def read_links_file(file_path: str) -> list:
    """Read URLs from the links file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        urls = [line.strip() for line in lines if line.strip() and line.strip().startswith('http')]
        
        return urls
    
    except FileNotFoundError:
        console.print(f"[red]✗[/red] Links file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error reading links file: {e}")
        sys.exit(1)


def process_property(url: str, scraper: PropertyScraper, processor: LLMProcessor, db: PropertyDatabase) -> str:
    """
    Process a single property: scrape, extract data with LLM, save to DB.
    Returns 'inserted', 'updated', or 'failed'.
    """
    try:
        # Step 1: Scrape
        logger.info("Step 1: Scraping property page...")
        scraped_data = scraper.scrape_property(url)
        console.print(f"  [green]✓[/green] Scraped {len(scraped_data['text'])} characters")
        
        # Step 2: LLM Processing
        logger.info("Step 2: Processing with LLM...")
        extracted_data = processor.process_property(scraped_data)
        console.print(f"  [green]✓[/green] Extracted {len(extracted_data)} fields")
        
        # Step 3: Calculate fields
        logger.info("Step 3: Calculating derived fields...")
        from src.utils.calculated_fields import calculate_all_fields
        extracted_data = calculate_all_fields(extracted_data)
        
        # Step 4: Save to database
        logger.info("Step 4: Saving to database...")
        status = db.upsert_property(extracted_data)
        
        if status == 'inserted':
            console.print(f"  [green]✓[/green] Successfully inserted new property")
        elif status == 'updated':
            console.print(f"  [blue]🔄[/blue] Successfully updated existing property")
        
        return status
    
    except Exception as e:
        error_msg = str(e)
        
        # Handle specific error types with user-friendly messages
        if "Read timed out" in error_msg or "timed out" in error_msg.lower():
            console.print(f"  [yellow]⏱[/yellow] Timeout: LLM took too long to respond (>120s)")
            console.print(f"  [dim]💡 Tip: Try using a faster model or increase timeout in config[/dim]")
        elif "Connection refused" in error_msg or "Failed to connect" in error_msg:
            console.print(f"  [red]✗[/red] Connection Error: Is Ollama running?")
            console.print(f"  [dim]💡 Run: ollama serve[/dim]")
        else:
            console.print(f"  [red]✗[/red] Error: {error_msg[:100]}")
        
        # Log full error for debugging (but don't show traceback to user)
        logger.error(f"Failed to process property: {error_msg}", exc_info=False)
        
        return 'failed'


def main():
    """Main application entry point."""
    # Header
    console.print()
    console.print(Panel.fit(
        "[bold cyan]WEB HOUSE SCRAPER[/bold cyan]",
        box=box.DOUBLE,
        border_style="cyan"
    ))
    console.print()
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        console.print("[yellow]⚠[/yellow]  .env file not found. Using default configuration.")
    
    # Initialize components
    console.print("[bold]Initializing components...[/bold]")
    scraper = PropertyScraper()
    processor = LLMProcessor()
    db = PropertyDatabase()
    console.print("[green]✓[/green] All components initialized\n")
    
    # Read links
    links_file = config.LINKS_FILE
    urls = read_links_file(links_file)
    
    if not urls:
        console.print("[red]✗[/red] No URLs found in links file")
        sys.exit(1)
    
    # Stats
    stats = {
        'total': len(urls),
        'inserted': 0,
        'updated': 0,
        'failed': 0
    }
    
    # Process properties
    console.print(f"[bold]Processing {len(urls)} properties...[/bold]\n")
    
    for i, url in enumerate(urls, 1):
        console.print(f"\n[bold cyan]═══ [{i}/{stats['total']}] ═══[/bold cyan]")
        console.print(f"[dim]{url}[/dim]")
        
        try:
            status = process_property(url, scraper, processor, db)
            
            if status == 'inserted':
                stats['inserted'] += 1
            elif status == 'updated':
                stats['updated'] += 1
            elif status == 'failed':
                stats['failed'] += 1
        
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠[/yellow] Interrupted by user")
            break
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
            stats['failed'] += 1
    
    # Summary table
    console.print()
    table = Table(title="[bold]SUMMARY[/bold]", box=box.ROUNDED, border_style="cyan")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="bold")
    
    table.add_row("Total URLs", str(stats['total']))
    table.add_row("New properties", f"[green]{stats['inserted']}[/green]")
    table.add_row("Updated properties", f"[blue]{stats['updated']}[/blue]")
    table.add_row("Failed", f"[red]{stats['failed']}[/red]")
    table.add_row("", "")
    table.add_row("Total in database", str(db.count_properties()))
    
    console.print(table)
    console.print(f"\n[dim]Database: {config.DATABASE_FILE}[/dim]\n")
    
    db.close()


if __name__ == "__main__":
    main()

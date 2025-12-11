"""
Core pipeline logic for the scraper application.
"""
import sys
import logging
from rich.console import Console
from src.core.scraper import PropertyScraper
from src.core.llm_processor import LLMProcessor
from src.database.database import PropertyDatabase
from src.utils import config, status_manager

logger = logging.getLogger(__name__)
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

def run_scraping_pipeline(skip_existing: bool = False):
    """
    Run the main scraping pipeline.
    
    Args:
        skip_existing: If True, skip URLs that are already in the database.
    """
    # Initialize components
    console.print("[bold]Initializing components...[/bold]")
    scraper = PropertyScraper()
    processor = LLMProcessor()
    db = PropertyDatabase()
    console.print("[green]✓[/green] All components initialized\n")
    
    # STEP 1: Sync statuses from properties-status.md to database (HYBRID APPROACH)
    console.print("[bold]Step 1: Syncing existing statuses...[/bold]")
    updated, skipped = status_manager.sync_status_to_db(db)
    console.print(f"[green]✓[/green] Synced {updated} statuses to database\n")
    
    # STEP 2: Read links from inbox
    console.print("[bold]Step 2: Reading links from inbox...[/bold]")
    urls = status_manager.get_links_from_inbox()
    
    if not urls:
        console.print("[yellow]ℹ[/yellow] No URLs found in inbox (links-to-scrap.md)")
        console.print("[dim]Add URLs to data/links-to-scrap.md to scrape properties[/dim]\n")
        db.close()
        return
    
    console.print(f"[green]✓[/green] Found {len(urls)} URLs to process\n")
    
    # Stats
    stats = {
        'total': len(urls),
        'inserted': 0,
        'updated': 0,
        'failed': 0,
        'skipped': 0,
        'moved_to_tracking': 0
    }
    
    # Process properties
    console.print(f"[bold]Processing {len(urls)} properties...[/bold]\n")
    
    for i, url in enumerate(urls, 1):
        console.print(f"\n[bold cyan]═══ [{i}/{stats['total']}] ═══[/bold cyan]")
        console.print(f"[dim]{url}[/dim]")
        
        if skip_existing:
            existing_prop = db.get_property_by_url(url)
            if existing_prop:
                console.print("  [yellow]⏭[/yellow] Skipping existing property")
                stats['skipped'] += 1
                continue

        try:
            status = process_property(url, scraper, processor, db)
            
            if status == 'inserted':
                stats['inserted'] += 1
                # Add to tracking file and remove from inbox
                status_manager.append_to_status_file(url, '')
                status_manager.remove_from_inbox(url)
                stats['moved_to_tracking'] += 1
            elif status == 'updated':
                stats['updated'] += 1
                # Also add to tracking if not there and remove from inbox
                status_manager.append_to_status_file(url, '')
                status_manager.remove_from_inbox(url)
                stats['moved_to_tracking'] += 1
            elif status == 'failed':
                stats['failed'] += 1
        
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠[/yellow] Interrupted by user")
            break
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
            stats['failed'] += 1
    
    # Summary table
    from rich.table import Table
    from rich import box
    
    console.print()
    table = Table(title="[bold]SUMMARY[/bold]", box=box.ROUNDED, border_style="cyan")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="bold")
    
    table.add_row("Total URLs", str(stats['total']))
    table.add_row("New properties", f"[green]{stats['inserted']}[/green]")
    table.add_row("Updated properties", f"[blue]{stats['updated']}[/blue]")
    table.add_row("Skipped", f"[yellow]{stats['skipped']}[/yellow]")
    table.add_row("Failed", f"[red]{stats['failed']}[/red]")
    table.add_row("", "")
    table.add_row("Total in database", str(db.count_properties()))
    
    console.print(table)
    console.print(f"\n[dim]Database: {config.DATABASE_FILE}[/dim]\n")
    
    db.close()

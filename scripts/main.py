#!/usr/bin/env python3
"""
Main application CLI using Typer.
"""
import sys
import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.pipeline import run_scraping_pipeline
from src.utils.viewer import view_database, show_stats
from src.utils.exporter import export_to_csv
from src.utils import status_manager
from src.database.database import PropertyDatabase

app = typer.Typer(
    name="web-house-scraper",
    help="CLI tool to scrape property listings and manage the database.",
    add_completion=False
)
console = Console()

@app.command()
def export(
    output: str = typer.Option(
        "data/properties_export.csv",
        "--output",
        "-o",
        help="Path to the primary output CSV file."
    )
):
    """
    Export database to CSV.
    """
    export_to_csv(output)
    
    # Also sync to docs/ for the web interface
    if output == "data/properties_export.csv":
        docs_path = "docs/properties_export.csv"
        import shutil
        try:
            shutil.copy2(output, docs_path)
            console.print(f"[green]✓[/green] Synced export to [bold]{docs_path}[/bold]")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to sync to docs: {e}")

@app.command()
def stats():
    """
    Show database statistics.
    """
    show_stats()

@app.command()
def scrape(
    skip_existing: bool = typer.Option(
        False, 
        "--skip-existing", 
        "-s", 
        help="Skip URLs that are already in the database."
    )
):
    """
    Scrape properties from the links file.
    """
    status_manager.ensure_data_files_exist()
    run_scraping_pipeline(skip_existing=skip_existing)

@app.command()
def view(
    status: str = typer.Option(
        None,
        "--status",
        "-st",
        help="Filter by status: blank, YES, NO, MAYBE"
    )
):
    """
    View properties stored in the database.
    """
    view_database(status=status)

@app.command(name="sync-status")
def sync_status():
    """
    Sync property statuses from properties-status.md to database.
    """
    status_manager.ensure_data_files_exist()
    try:
        with PropertyDatabase() as db:
            console.print("[cyan]Syncing statuses from properties-status.md...[/cyan]")
            updated, skipped = status_manager.sync_status_to_db(db)
            
            console.print()
            console.print(f"[green]✓[/green] Status sync complete:")
            console.print(f"  Updated: {updated}")
            console.print(f"  Skipped: {skipped}")
            console.print()
    except Exception as e:
        console.print(f"[red]Error syncing statuses: {e}[/red]")
        raise typer.Exit(code=1)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Web House Scraper CLI
    """
    # Header
    console.print()
    console.print(Panel.fit(
        "[bold cyan]WEB HOUSE SCRAPER[/bold cyan]",
        box=box.DOUBLE,
        border_style="cyan"
    ))
    console.print()
    
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        console.print("[yellow]Tip: Run with --help to see available commands[/yellow]")
        # We can also default to scrape if desired, but explicit is better for CLI tools
        # ctx.invoke(scrape, skip_existing=False)

if __name__ == "__main__":
    app()

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
        help="Path to the output CSV file."
    )
):
    """
    Export database to CSV.
    """
    export_to_csv(output)

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
    run_scraping_pipeline(skip_existing=skip_existing)

@app.command()
def view():
    """
    View properties stored in the database.
    """
    view_database()

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

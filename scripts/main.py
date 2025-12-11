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

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.scraper import PropertyScraper
from src.core.llm_processor import LLMProcessor
from src.database.database import PropertyDatabase
from src.utils import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_links_file(file_path: str) -> list:
    """Read URLs from the links file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter out empty lines and strip whitespace
        urls = [line.strip() for line in lines if line.strip() and line.strip().startswith('http')]
        
        logger.info(f"Found {len(urls)} URLs in {file_path}")
        return urls
    
    except FileNotFoundError:
        logger.error(f"Links file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading links file: {e}")
        sys.exit(1)


def process_property(url: str, scraper: PropertyScraper, processor: LLMProcessor, db: PropertyDatabase) -> str:
    """
    Process a single property: scrape, extract data with LLM, save to DB.
    Returns 'inserted', 'updated', or 'failed'.
    """
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {url}")
        logger.info(f"{'='*80}")
        
        # Step 1: Scrape the property page
        logger.info("Step 1: Scraping property page...")
        scraped_data = scraper.scrape_property(url)
        logger.info(f"✓ Scraped {len(scraped_data['text'])} characters of text")
        
        # Step 2: Process with LLM
        logger.info("Step 2: Processing with LLM...")
        extracted_data = processor.process_property(scraped_data)
        logger.info(f"✓ Extracted data: {list(extracted_data.keys())}")
        
        # Step 3: Save to database (UPSERT)
        logger.info("Step 3: Saving to database...")
        status = db.upsert_property(extracted_data)
        
        if status == 'inserted':
            logger.info(f"✓ Successfully inserted new property")
        elif status == 'updated':
            logger.info(f"✓ Successfully updated existing property")
        
        return status
    
    except Exception as e:
        logger.error(f"✗ Failed to process property: {e}")
        logger.exception(e)
        return 'failed'


def main():
    """Main application entry point."""
    print("\n" + "="*80)
    print("WEB HOUSE SCRAPER")
    print("="*80 + "\n")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("⚠ .env file not found. Using default configuration.")
        logger.info("💡 Copy .env.example to .env to customize settings.")
    
    # Initialize components
    logger.info("Initializing components...")
    scraper = PropertyScraper()
    processor = LLMProcessor()
    db = PropertyDatabase()
    
    # Read links
    links_file = config.LINKS_FILE
    urls = read_links_file(links_file)
    
    if not urls:
        logger.error("No URLs found in links file")
        sys.exit(1)
    
    # Process each property
    print(f"\nProcessing {len(urls)} properties...\n")
    
    stats = {
        'total': len(urls),
        'inserted': 0,
        'updated': 0,
        'failed': 0
    }
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{stats['total']}] Processing: {url}")
        
        try:
            status = process_property(url, scraper, processor, db)
            
            if status == 'inserted':
                stats['inserted'] += 1
            elif status == 'updated':
                stats['updated'] += 1
            elif status == 'failed':
                stats['failed'] += 1
        
        except KeyboardInterrupt:
            logger.warning("\n⚠ Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            stats['failed'] += 1
            continue
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total URLs:           {stats['total']}")
    print(f"New properties:       {stats['inserted']}")
    print(f"Updated properties:   {stats['updated']}")
    print(f"Failed:               {stats['failed']}")
    print(f"\nDatabase: {config.DATABASE_FILE}")
    print(f"Total properties in DB: {db.count_properties()}")
    print("="*80 + "\n")
    
    db.close()


if __name__ == "__main__":
    main()

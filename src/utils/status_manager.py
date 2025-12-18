"""
Status manager module for handling property status tracking.
Manages reading/writing from properties-status.md and links-to-scrap.md.
"""

import os
import re
import logging
from typing import Dict, List, Tuple
from pathlib import Path
from src.utils import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# File paths
LINKS_FILE = config.DATA_DIR / "links-to-scrap.md"
STATUS_FILE = config.DATA_DIR / "properties-status.md"

# Status regex pattern: matches [ ], [YES], [NO], [MAYBE]
STATUS_PATTERN = re.compile(r'^\[(.*?)\]\s+(https?://\S+)', re.MULTILINE)


def ensure_data_files_exist():
    """
    Check if required data files exist. If not, print error and exit.
    """
    from rich.console import Console
    from rich.panel import Panel
    import sys
    
    console = Console()
    missing_files = []
    
    if not LINKS_FILE.exists():
        missing_files.append(("links-to-scrap.md", "links-to-scrap-example.md"))
    
    if not STATUS_FILE.exists():
        missing_files.append(("properties-status.md", "properties-status-example.md"))
        
    if missing_files:
        console.print()
        for real, example in missing_files:
            console.print(Panel(
                f"[red]✗[/red] Required file missing: [bold]data/{real}[/bold]\n\n"
                f"[yellow]To fix this, create the file from the example:[/yellow]\n"
                f"[cyan]cp data/{example} data/{real}[/cyan]",
                title="[bold red]Missing Configuration[/bold red]",
                border_style="red"
            ))
        console.print()
        sys.exit(1)


def parse_status_file() -> Dict[str, str]:
    """
    Parse properties-status.md and extract URL → status mapping.
    
    Returns:
        Dict mapping URLs to status ('', 'YES', 'NO', 'MAYBE')
    """
    if not STATUS_FILE.exists():
        logger.warning(f"Status file not found: {STATUS_FILE}")
        return {}
    
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        status_map = {}
        matches = STATUS_PATTERN.findall(content)
        
        for status_text, url in matches:
            # Clean status text (strip whitespace)
            status = status_text.strip()
            # Normalize to empty string for blank status
            if not status:
                status = ''
            status_map[url] = status
        
        logger.info(f"Parsed {len(status_map)} properties from status file")
        return status_map
        
    except Exception as e:
        logger.error(f"Failed to parse status file: {e}")
        return {}


def sync_status_to_db(db) -> Tuple[int, int]:
    """
    Sync statuses from properties-status.md to database.
    
    Args:
        db: PropertyDatabase instance
    
    Returns:
        Tuple of (updated_count, skipped_count)
    """
    status_map = parse_status_file()
    
    if not status_map:
        logger.warning("No statuses to sync")
        return 0, 0
    
    updated = 0
    skipped = 0
    
    for url, status in status_map.items():
        # Check if property exists
        existing = db.get_property_by_url(url)
        if existing:
            # Only update if status changed
            if existing.get('status', '') != status:
                if db.update_status(url, status):
                    updated += 1
                else:
                    skipped += 1
        else:
            skipped += 1
            logger.debug(f"Property not in DB, skipped: {url}")
    
    logger.info(f"Status sync complete: {updated} updated, {skipped} skipped")
    return updated, skipped


def append_to_status_file(url: str, status: str = '') -> bool:
    """
    Append a new URL to properties-status.md with given status.
    
    Args:
        url: Property URL
        status: Status tag ('', 'YES', 'NO', 'MAYBE')
    
    Returns:
        True if successful
    """
    try:
        # Create file if it doesn't exist
        if not STATUS_FILE.exists():
            _create_status_file()
        
        # Check if URL already exists
        existing_statuses = parse_status_file()
        if url in existing_statuses:
            logger.debug(f"URL already in status file: {url}")
            return True
        
        # Format status tag
        status_tag = f"[{status}]" if status else "[ ]"
        
        # Append to file
        with open(STATUS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{status_tag} {url}\n")
        
        logger.info(f"Added to status file: {status_tag} {url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to append to status file: {e}")
        return False


def remove_from_inbox(url: str) -> bool:
    """
    Remove a URL from links-to-scrap.md after processing.
    
    Args:
        url: URL to remove
    
    Returns:
        True if successful
    """
    if not LINKS_FILE.exists():
        return True
    
    try:
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter out the URL (and blank lines)
        new_lines = [line for line in lines if url not in line]
        
        with open(LINKS_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        logger.info(f"Removed from inbox: {url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to remove from inbox: {e}")
        return False


def _create_status_file():
    """Create properties-status.md with header if it doesn't exist."""
    try:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        header = """# Property Status Tracking

<!-- Status tags: [ ] = Not reviewed, [YES] = Interested, [NO] = Not interested, [MAYBE] = Maybe -->

"""
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            f.write(header)
        
        logger.info(f"Created status file: {STATUS_FILE}")
        
    except Exception as e:
        logger.error(f"Failed to create status file: {e}")
        raise


def get_links_from_inbox() -> List[str]:
    """
    Read all URLs from links-to-scrap.md.
    
    Returns:
        List of URLs
    """
    if not LINKS_FILE.exists():
        logger.warning(f"Links file not found: {LINKS_FILE}")
        return []
    
    try:
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract URLs (filter out comments and blank lines)
        urls = []
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('<!--'):
                continue
            # Check if line contains URL
            if line.startswith('http'):
                urls.append(line)
        
        logger.info(f"Found {len(urls)} URLs in inbox")
        return urls
        
    except Exception as e:
        logger.error(f"Failed to read inbox file: {e}")
        return []

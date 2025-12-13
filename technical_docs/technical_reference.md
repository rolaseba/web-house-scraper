# Technical Reference Manual

## 1. System Overview

**Web House Scraper** is a hybrid data extraction system designed to collect real estate property data from websites like Zonaprop and Argenprop. It combines **structured extraction** (Regex/CSS) for high precision on numerical data with **LLM processing** (Ollama) for complex unstructured text.

### Key Features
- **Hybrid Extraction**: 100% precision on numbers, semantic understanding for text.
- **Anti-Scraping Bypass**: Automatic fallback from `requests` to `Playwright`.
- **UPSERT Logic**: Idempotent operations (safe to re-run).
- **Status Tracking**: Two-way sync between Markdown files and SQLite.

---

## 2. System Architecture

The system follows a modular pipeline architecture orchestrated by a CLI.

```mermaid
graph TD
    CLI[CLI (main.py)] --> Pipeline[Pipeline (pipeline.py)]
    
    subgraph "Data Acquisition"
        Pipeline --> Scraper[PropertyScraper]
        Scraper -->|HTML/Text| Processor[LLMProcessor]
    end
    
    subgraph "Data Processing"
        Processor --> Extractor[StructuredExtractor]
        Extractor -->|Partial Data| Processor
        Processor -->|Prompt| LLM[Ollama / Gemini]
        LLM -->|JSON| Processor
        Processor -->|Merged Data| Calculator[Calculated Fields]
    end
    
    subgraph "Storage & State"
        Pipeline --> DB[(SQLite Database)]
        Pipeline --> Status[StatusManager]
        Status <--> Files[Markdown Files]
    end
```

---

## 3. Core Components

### 3.1 PropertyScraper (`src/core/scraper.py`)
Responsible for fetching raw HTML from URLs.
- **Strategy**:
  1. Tries `requests` (fast, lightweight).
  2. If blocked (403/Timeout), falls back to `Playwright` (headless browser).
- **Cleaning**: Removes `<script>`, `<style>`, and other noise to optimize LLM token usage.

### 3.2 StructuredExtractor (`src/core/structured_extractor.py`)
Extracts data using deterministic rules defined in `data/site_configs.json`.
- **Methods**: Regex patterns and CSS selectors.
- **Purpose**: Handles fields like Price, Currency, Surface Area, and Room counts with 100% accuracy, bypassing the LLM to save time and reduce hallucinations.

### 3.3 LLMProcessor (`src/core/llm_processor.py`)
Orchestrates the data extraction process.
- **Workflow**:
  1. Calls `StructuredExtractor` first.
  2. Identifies missing fields.
  3. Constructs a prompt asking *only* for missing information.
  4. Calls LLM (Ollama/DeepSeek).
  5. Merges and validates results.

### 3.4 PropertyDatabase (`src/database/database.py`)
Manages the SQLite database (`data/properties.db`).
- **Schema**: Dynamic schema based on `config.EXTRACTION_FIELDS`.
- **UPSERT**: Uses `INSERT OR REPLACE` logic (via manual check) to update existing records without duplication.
- **Status Sync**: Maintains a `status` column synchronized with `properties-status.md`.

### 3.5 StatusManager (`src/utils/status_manager.py`)
Manages the user workflow files.
- **Inbox**: `data/links-to-scrap.md` (New URLs).
- **Tracking**: `data/properties-status.md` (Processed URLs with status).
- **Sync**: Parses `[YES]`, `[NO]`, `[MAYBE]` tags and updates the database.

---

## 4. Workflows

### 4.1 Scraping Pipeline
Triggered by `python scripts/main.py scrape`.

1. **Initialization**: Load config, connect to DB.
2. **Sync**: Update DB statuses from `properties-status.md`.
3. **Read Inbox**: Load URLs from `links-to-scrap.md`.
4. **Process Loop**:
   - **Scrape**: Fetch HTML.
   - **Extract**: Structured -> LLM -> Merge.
   - **Calculate**: Derive fields (e.g., price per m²).
   - **Save**: UPSERT into DB.
   - **Track**: Move URL from Inbox to Tracking file.
5. **Report**: Show summary stats.

### 4.2 Status Synchronization
Triggered by `python scripts/main.py sync-status` or automatically during scrape.

1. **Parse**: Read `data/properties-status.md`.
2. **Extract**: Find lines matching `[STATUS] URL`.
3. **Update**: For each URL, update the `status` column in SQLite.
4. **Result**: Database reflects manual decisions made in the Markdown file.

---

## 5. Configuration

### 5.1 Site Configurations (`data/site_configs.json`)
Defines how to extract data from specific domains.

```json
"zonaprop.com.ar": {
  "name": "Zonaprop",
  "patterns": {
    "precio": {
      "type": "regex",
      "pattern": "(?:USD|\\$)\\s*([\\d.,]+)"
    },
    "cantidad_dormitorios": {
      "type": "css_selector",
      "selector": ".section-icon-bedroom"
    }
  }
}
```

### 5.2 Environment Variables (`.env`)
- `LLM_PROVIDER`: `ollama` or `google`.
- `OLLAMA_MODEL`: Model name (e.g., `deepseek-r1:latest`).
- `OLLAMA_BASE_URL`: URL for Ollama API.

---

## 6. Directory Structure

- `src/core`: Business logic (Scraper, Processor).
- `src/database`: Data persistence.
- `src/utils`: Helpers (Config, Viewer, Exporter).
- `scripts`: Entry points (CLI).
- `data`: Runtime data (DB, Configs, Logs).

# Web House Scraper

Application to scrape real estate properties from Argenprop and Zonaprop, process the information with a **hybrid system** (structured extraction + local LLM) and save it in a SQLite database.

## Features

- 🔍 Property scraping from Argenprop and Zonaprop
- 🎯 **Hybrid Extraction System**:
  - Structured extraction with regex/CSS for numeric fields (100% precision)
  - LLM (Ollama) only for complex fields (addresses, descriptions)
- ⚙️ **Per-Site Configuration**: Patterns defined in `data/site_configs.json` (no code modification required)
- 🤖 Intelligent processing with LLM (Ollama or Google Gemini)
- 💾 SQLite storage with **UPSERT** functionality (insert/update)
- 🛡️ Anti-scraping handling via Playwright
- 📦 **Professional Structure**: Organized according to Python best practices

## Requirements

- Python 3.8+
- Ollama installed and running locally (default)
- Operating System: Linux, macOS, Windows

## Installation

1. **Clone the repository**

```bash
cd /home/seba/Documentos/Data\ Science\ Projects/web-house-scraper
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env if necessary
```

5. **Ensure Ollama is running**

```bash
1.  **Clone the repository**

    ```bash
    cd /home/seba/Documentos/Data\ Science\ Projects/web-house-scraper
    ```

2.  **Create virtual environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Configure environment variables**

    ```bash
    cp .env.example .env
    # Edit .env if necessary
    ```

5.  **Ensure Ollama is running**

    ```bash
    ollama serve  # In another terminal
    ollama pull deepseek-r1:latest  # Download the model
    ```

## Project Structure

```text
web-house-scraper/
│
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core logic
│   │   ├── scraper.py              # Web scraping
│   │   ├── llm_processor.py        # Hybrid LLM processing
│   │   └── structured_extractor.py # Structured extraction
│   │
│   ├── 📁 database/                 # Data layer
│   │   └── database.py             # SQLite with UPSERT
│   │
│   └── 📁 utils/                    # Utilities
│       ├── config.py               # Central configuration
│       └── status_manager.py       # Status file management
│
├── 📁 data/                         # Data and configurations
│   ├── properties.db               # SQLite database
│   ├── links-to-scrap.md          # URLs to process (INBOX)
│   ├── links-to-scrap-example.md  # Example URLs (VERSIONED)
│   ├── properties-status.md       # Status tracking (TRACKING)
│   ├── properties-status-example.md # Example statuses (VERSIONED)
│   └── site_configs.json          # Extraction patterns per site
│
├── 📁 scripts/                      # Executable scripts
│   └── main.py                     # Main CLI (Typer)
│
├── 📁 tests/                        # Tests (future proof)
│
├── .env                             # Environment variables (private)
├── .env.example                     # Configuration example
├── requirements.txt                 # Python dependencies
└── README.md                        # This documentation
```

## Quick Usage

### 1. Add URLs

Edit `data/links-to-scrap.md` and add URLs (one per line).
> [!TIP]
> If the file does not exist, you can create it by copying `data/links-to-scrap-example.md`.

```markdown
https://www.zonaprop.com.ar/propiedades/...
https://www.argenprop.com/departamento-en-venta...
```

### 2. Run the scraper

```bash
python scripts/main.py scrape
```

To skip existing properties:

```bash
python scripts/main.py scrape --skip-existing
```

### 3. View results

```bash
python scripts/main.py view
```

### 4. View statistics

```bash
python scripts/main.py stats
```

### 5. Export to CSV

```bash
python scripts/main.py export
```

Default saves to `data/properties_export.csv`. To change the file:

```bash
python scripts/main.py export --output my_file.csv
```

### 6. Property Status Tracking

#### Two-File System

The system uses two markdown files to organize your workflow:

- **`data/links-to-scrap.md`** - **INBOX**: New URLs to scrape (temporary)
- **`data/properties-status.md`** - **TRACKING**: All properties with review status (permanent)

> [!NOTE]
> These files are ignored by Git to keep your data private. Examples of these files are provided as `data/links-to-scrap-example.md` and `data/properties-status-example.md`. You should create the real files from these examples.

#### Mark Properties

Edit `data/properties-status.md` and change the statuses:

```markdown
[ ] https://www.zonaprop.com.ar/...  # Not reviewed
[YES] https://www.zonaprop.com.ar/... # Interested
[NO] https://www.argenprop.com/...    # Not interested
[MAYBE] https://www.zonaprop.com.ar/... # Maybe
```

#### Sync Statuses

```bash
# Option 1: Sync manually
python scripts/main.py sync-status

# Option 2: Auto-sync when scraping
python scripts/main.py scrape  # Automatically syncs before scraping
```

#### Filter by Status

```bash
# View only interested properties
python scripts/main.py view --status YES

# View discarded properties
python scripts/main.py view --status NO

# View "maybe"
python scripts/main.py view --status MAYBE

# View not reviewed
python scripts/main.py view --status blank
```

#### Complete Workflow

1. Add URLs to `data/links-to-scrap.md`
2. Run `python scripts/main.py scrape`
   - ✅ Scrapes properties
   - ✅ Automatically moves them to `properties-status.md` with status `[ ]`
   - ✅ Automatically clears `links-to-scrap.md`
3. Edit statuses in `properties-status.md`
4. Next time you run `scrape`, it syncs automatically

### 7. Help

To see all available commands:

```bash
python scripts/main.py --help
```

Or specific command help:

```bash
python scripts/main.py scrape --help
```

Or access the database directly:

```bash
sqlite3 data/properties.db "SELECT * FROM properties;"
```

## Configuration

### Extracted Fields

The system automatically extracts **21 fields** (defined in `src/utils/config.py`):

**Basic:**
- `tipo_operacion` (sale/rent)
- `tipo_inmueble` (house/apartment)
- `direccion` (address)
- `barrio` (neighborhood)

**Measurements:**
- `metros_cuadrados_cubiertos` (covered sq meters)
- `metros_cuadrados_totales` (total sq meters)
- `precio` (price)
- `moneda` (currency USD/ARS)

**Distribution:**
- `cantidad_dormitorios` (bedrooms)
- `cantidad_banos` (bathrooms)
- `cantidad_ambientes` (rooms)

**Boolean Features:**
- `tiene_patio` (has patio)
- `tiene_quincho` (has bbq area)
- `tiene_pileta` (has pool)
- `tiene_cochera` (has garage)
- `tiene_balcon` (has balcony)
- `tiene_terraza` (has terrace)

**Additional Details:**
- `piso` (floor: PB, 1, 2, 3... or 0 for houses)
- `orientacion` (orientation: North, South, East, West)
- `antiguedad` (age)
- `descripcion_breve` (short description)

### Environment Variables (.env)

```bash
LLM_PROVIDER=ollama                      # ollama or google
OLLAMA_MODEL=deepseek-r1:latest         # Ollama model
OLLAMA_BASE_URL=http://localhost:11434  # Ollama base URL
GOOGLE_API_KEY=                         # To use Gemini (optional)
GEMINI_MODEL=gemini-pro                 # Gemini model
```

## Hybrid Extraction System

The application uses a **two-step** approach for maximum precision and efficiency:

### Step 1: Structured Extraction

First extracts fields using **regex/CSS patterns** defined in `data/site_configs.json`:

✅ **100% precision** in:
- Price
- Currency
- Square meters (covered and total)
- Number of bedrooms/bathrooms
- Operation type (sale/rent)

### Step 2: LLM Processing

Then uses the **LLM only for complex fields**:
- Full address
- Neighborhood/zone
- Features (patio, bbq, pool, balcony, terrace, etc.)
- Property type
- Orientation
- Floor
- Short description
- Age

### Advantages

- ⚡ **100% precision** in numeric fields
- 🚀 **Faster**: LLM processes only ~40% of fields
- 🔧 **Maintainable**: Patterns in JSON, not in code
- 📈 **Scalable**: Easy to add new sites

### Add New Site

Edit `data/site_configs.json` and add configuration:

```json
{
  "newsite.com": {
    "name": "New Site",
    "structured_fields": ["precio", "moneda", "cantidad_dormitorios"],
    "llm_fields": ["direccion", "barrio", "descripcion_breve"],
    "patterns": {
      "precio": {
        "type": "regex",
        "pattern": "(?:USD|ARS)\\s*([\\d.,]+)",
        "search_in": "text"
      },
      "cantidad_dormitorios": {
        "type": "css",
        "selector": ".bedrooms-count",
        "attribute": "text"
      }
    }
  }
}
```

## UPSERT Functionality

The system implements automatic **UPSERT** (Update or Insert):

### Behavior

When you run the app with a link that already exists in the database:

- ✅ Property is **updated** with new extracted data
- ✅ `scraped_at` timestamp is **updated** automatically
- ✅ Terminal clearly shows: `🔄 Updated property`
- ✅ Final summary distinguishes between "New properties" and "Updated properties"

### Output Example

```text
[1/5] Processing: https://www.zonaprop.com.ar/...
INFO:src.database.database:🔄 Updated property: https://www.zonaprop.com.ar/...
INFO:__main__:✓ Successfully updated existing property

SUMMARY
================================================================================
Total URLs:           5
New properties:       0
Updated properties:   5    👈 All updated
Failed:               0
```

### Use Cases

- 📊 Update changing prices
- 🔄 Refresh modified features
- 📈 Track properties over time
- 🔍 Continuous market monitoring

## Troubleshooting

### Error: "externally-managed-environment"

**Solution**: Use virtual environment (see installation).

### Error: "Links file not found"

**Cause**: File `data/links-to-scrap.md` does not exist or is empty.

**Solution**:
Create the file from the example:

```bash
cp data/links-to-scrap-example.md data/links-to-scrap.md
```

Or add a link manually:

```bash
echo "https://www.zonaprop.com.ar/..." > data/links-to-scrap.md
```

### Scraping Timeout

**Cause**: Some pages may take time to load.

**Solution**: Adjust timeout in `src/core/scraper.py` (line ~40).

### LLM not responding

**Verify Ollama is running**:
```bash
ollama list  # View installed models
ollama serve # Start server
```

### Error 403 Forbidden

**Normal**: Zonaprop uses anti-scraping protection.

**Automatic Solution**: System uses Playwright as fallback (already implemented).

## Important Notes

- 🔒 **Anti-scraping**: Zonaprop uses 403 protection → Automatically resolved with Playwright
- 🤖 **Local LLM**: Ensure Ollama is running: `ollama serve`
- 📦 **Model**: Defaults to `deepseek-r1:latest` → Download with: `ollama pull deepseek-r1:latest`
- 💰 **Paid APIs**: To use Google Gemini, configure `GOOGLE_API_KEY` in `.env`
- 🔄 **UPSERT**: Re-running with same links **updates** data automatically
- 📁 **Structure**: Project organized according to Python best practices (src/, data/, scripts/)

## Execution Examples

### Activate environment and run

```bash
cd /home/seba/Documentos/Data\ Science\ Projects/web-house-scraper
source venv/bin/activate
python scripts/main.py scrape
```

### View formatted properties

```bash
python scripts/main.py view
```

### Direct SQL query

```bash
sqlite3 data/properties.db
> SELECT direccion, precio, moneda, cantidad_dormitorios FROM properties;
> .quit
```

## Contributing

To contribute to the project:

1. Create feature branch
2. Add tests in `tests/`
3. Update documentation if necessary
4. Submit pull request

## License

MIT

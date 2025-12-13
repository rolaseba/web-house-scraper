# Adding New Sites for Structured Scraping

This guide explains how to configure the scraper to extract structured data from new real estate websites. Structured extraction is preferred over pure LLM extraction because it is faster, cheaper, and more accurate for specific fields like price and area.

## Workflow Overview

1.  **Analyze the Page**: Determine how the data is structured in the HTML.
2.  **Choose Strategy**: Decide between CSS Selectors (standard) or Regex (for scripts/JSON).
3.  **Update Configuration**: Add the site to `data/site_configs.json`.
4.  **Verify**: Test the extraction.

---

## 1. Analyze the Page

Before writing code, you need to find where the data lives.

### Tools
-   **Browser DevTools (F12)**: Use the "Inspector" to click on elements (Price, Address) and see their HTML tags and classes.
-   **View Page Source (Ctrl+U)** or `curl`: **Crucial step.** Sometimes what you see in DevTools is rendered by JavaScript and doesn't exist in the raw HTML fetched by the scraper.
    -   *Check*: Search for the price in the "View Source" tab. If it's there inside a `<div>`, use CSS selectors. If it's inside a `<script>` tag or JSON blob, use Regex.

### Example Case: Ficha.info
In `ficha.info`, the data wasn't in simple HTML tags in the raw source. It was inside a JSON blob:
```json
"Sale":["USD 290.000"]
```
This required a **Regex** strategy instead of CSS selectors.

---

## 2. Update Configuration

The core file to modify is:
`data/site_configs.json`

Add a new entry for your domain (e.g., `example.com`).

### Configuration Structure

```json
"example.com": {
    "name": "Example Site",
    "patterns": {
        "field_name": {
            "type": "css_selector | regex",
            "selector": ".price-tag",      // For css_selector
            "pattern": "Price: (\\d+)",    // For regex
            "search_in": "html | text",    // Where to look
            "transform": { ... }           // Optional value mapping
        }
    }
}
```

### Field Types

#### A. CSS Selector (Standard)
Best when data is in standard HTML tags.
```json
"precio": {
    "type": "css_selector",
    "selector": ".price-container .amount",
    "regex": "([\\d.,]+)"  // Optional: Extract number from text like "$ 100.000"
}
```

#### B. Regex (Advanced)
Best for data inside scripts, JSON blobs, or complex text.
```json
"precio": {
    "type": "regex",
    "pattern": "\"price\":\\s*(\\d+)",
    "search_in": "html"
}
```
*Note: In JSON strings, you often need to escape quotes, e.g., `\\\"price\\\"`.*

### Common Fields to Extract
-   `precio`
-   `moneda` (USD, ARS)
-   `metros_cuadrados_totales`
-   `metros_cuadrados_cubiertos`
-   `cantidad_dormitorios`
-   `cantidad_banos`
-   `tipo_operacion` (venta, alquiler)
-   `direccion`

---

## 3. Real Examples

### Example 1: Simple HTML (Argenprop)
Data is in a `div` with class `titlebar__price`.
```json
"precio": {
    "type": "css_selector",
    "selector": ".titlebar__price",
    "extract": "text",
    "regex": "([\\d.,]+)"
}
```

### Example 2: Hidden JSON Data (Ficha.info)
Data is inside a Next.js hydration script. We use regex to find the JSON key-value pair.
```json
"precio": {
    "type": "regex",
    "pattern": "\\\\\"Sale\\\\\":\\[\\\\\"(?:USD|ARS|\\$)\\s*([\\d.,]+)\\\\\"\\]",
    "search_in": "html"
}
```

---

## 4. Modifying Core Scraper Logic

Sometimes configuration isn't enough. You might need to modify `src/core/scraper.py` if:

1.  **The site blocks `requests`**: You need to adjust headers or fallback to Playwright.
2.  **The content is empty**:
    *   *Check*: In `scraper.py`, we added logic to check `len(html)`.
    ```python
    if html and len(html) < 1000:
        # Trigger fallback to browser
        html = None 
    ```

### How to Debug
1.  Create a reproduction script (like `reproduce_issue.py`) that imports `PropertyScraper`.
2.  Print `len(html)` to see if you are getting the full page.
3.  Save the HTML to a file (`debug.html`) and search for your data.

## Summary Checklist
1.  [ ] Verify data existence in "View Source".
2.  [ ] Add entry to `data/site_configs.json`.
3.  [ ] Run scraper on a test URL.
4.  [ ] If it fails, check `scraper.py` for blocking issues.

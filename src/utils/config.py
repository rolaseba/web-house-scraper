"""
Configuration module for the web house scraper.
Contains LLM settings and extraction field definitions.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get project root directory (two levels up from src/utils/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = Path(PROJECT_ROOT) / "data"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Options: "ollama", "google"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:latest")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# Database configuration
DATABASE_FILE = os.path.join(PROJECT_ROOT, "data", "properties.db")
LINKS_FILE = os.path.join(PROJECT_ROOT, "data", "links-to-scrap.md")

# Fields to extract from property listings
EXTRACTION_FIELDS = [
    "tipo_operacion",  # venta o alquiler
    "tipo_inmueble",  # casa o departamento
    "direccion",
    "barrio",
    "metros_cuadrados_cubiertos",
    "metros_cuadrados_totales",
    "precio",
    "moneda",  # USD, ARS, etc.
    "cantidad_dormitorios",
    "cantidad_banos",
    "cantidad_ambientes",  # cantidad de ambientes (si se menciona)
    "tiene_patio",  # boolean
    "tiene_quincho",  # boolean
    "tiene_pileta",  # boolean
    "tiene_cochera",  # boolean
    "tiene_balcon",  # boolean
    "tiene_terraza",  # boolean
    "piso",  # PB, 1, 2, 3, etc. (0 para casas)
    "orientacion",  # Sur, Norte, Este, Oeste, etc.
    "antiguedad",
    "descripcion_breve",
    "costo_metro_cuadrado",  # CALCULADO: precio / m2 ponderados
]

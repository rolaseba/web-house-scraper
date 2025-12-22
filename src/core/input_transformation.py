"""
Module for standardizing and transforming extracted property data.
Uses Pydantic for robust validation and modular transformations.
"""

import re
import logging
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator, field_validator, model_validator
from src.utils import config

logger = logging.getLogger(__name__)

class PropertyStandardizer(BaseModel):
    """Pydantic model for property data with custom validators for standardization."""
    
    tipo_operacion: Optional[str] = None
    tipo_inmueble: Optional[str] = None
    direccion: Optional[str] = None
    barrio: Optional[str] = None
    metros_cuadrados_cubiertos: Optional[float] = None
    metros_cuadrados_totales: Optional[float] = None
    precio: Optional[float] = None
    moneda: Optional[str] = None
    cantidad_dormitorios: Optional[int] = None
    cantidad_banos: Optional[int] = None
    cantidad_ambientes: Optional[int] = None
    tiene_patio: Optional[bool] = None
    tiene_quincho: Optional[bool] = None
    tiene_pileta: Optional[bool] = None
    tiene_cochera: Optional[bool] = None
    tiene_balcon: Optional[bool] = None
    tiene_terraza: Optional[bool] = None
    piso: Optional[str] = None
    orientacion: Optional[str] = None
    antiguedad: Optional[Union[str, int, float]] = None
    
    @field_validator("tipo_operacion", "tipo_inmueble", mode="before")
    @classmethod
    def standardize_lowercase(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True):
            return v
        if isinstance(v, str):
            return v.lower().strip()
        return v

    @field_validator("moneda", mode="before")
    @classmethod
    def standardize_uppercase(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True):
            return v
        if isinstance(v, str):
            return v.upper().strip()
        return v

    @field_validator("direccion", mode="before")
    @classmethod
    def standardize_direccion(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True) or not v:
            return v
        
        # Clean address: extract Street + Number
        # Removes things like "'09-01", "Piso 4", neighborhoods, cities
        # Example: "3 De Febrero 1208 '09-01, Centro, Rosario" -> "3 De Febrero 1208"
        # Example: "Moreno al 400" -> "Moreno 400"
        
        if not isinstance(v, str):
            return v
            
        address = v.strip()
        
        # Replace "al" with empty space if it's "Calle al 123"
        address = re.sub(r'\s+al\s+', ' ', address, flags=re.IGNORECASE)
        
        # Try to match typical address patterns: Street Name + Number
        # This regex looks for a name followed by a number, and stops there.
        match = re.search(r'^([^,]+?\d+)', address)
        if match:
            clean_address = match.group(1).strip()
            # Remove trailing quotes or punctuation
            clean_address = re.sub(r'[\'\",\.]$', '', clean_address).strip()
            return clean_address
            
        return address

    @field_validator("piso", mode="before")
    @classmethod
    def standardize_piso(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True) or v is None:
            return v
        
        if isinstance(v, str):
            v_lower = v.lower().strip()
            # List of negative assertions that should be null
            if v_lower in ["ninguno", "no especifica", "n/a", "null", "-", "piso", "ningun", "no", "no tiene"]:
                return None
            
            # If it's "planta baja" or "pb", standardize to "PB"
            if v_lower in ["pb", "planta baja", "p.b.", "0"]:
                return "PB"
                
            return v.strip()
        return v

    @field_validator("antiguedad", mode="before")
    @classmethod
    def standardize_antiguedad(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True) or v is None:
            return v
            
        v_str = str(v).lower().strip()
        
        # Positive list for 0 (new)
        if any(x in v_str for x in ["a estrenar", "nuevo", "estreno", "0 años", "0 años", "minimal"]):
            return 0
            
        # Extract number if present
        match = re.search(r'(\d+)', v_str)
        if match:
            return int(match.group(1))
            
        # If it's just text without numbers and not in positive list, return None or keep as is?
        # User recommended null if not detailed.
        return None

    @field_validator("precio", "metros_cuadrados_cubiertos", "metros_cuadrados_totales", mode="before")
    @classmethod
    def standardize_numeric(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True) or v is None:
            return v
        if isinstance(v, str):
            # Remove symbols and units
            v = re.sub(r'\$|USD|ARS|EUR|m2|mt2|metros|cuadrados', '', v, flags=re.IGNORECASE).strip()
            
            if not v:
                return None
                
            # Handle comma as decimal separator and dot as thousands separator (common in LatAm)
            # If there's a comma and dots, the dots are thousands separators.
            # Example: "180.000" -> "180000"
            # Example: "120,50" -> "120.50"
            # Example: "1.234.567,89" -> "1234567.89"
            
            if ',' in v and '.' in v:
                # Both separators present: remove dots, replace comma with dot
                v = v.replace('.', '').replace(',', '.')
            elif ',' in v:
                # Only comma present: if it's followed by 2 or 3 digits at the end, it might be decimal
                # But it could also be a thousands separator in US format. 
                # In the context of this app (Rosario, Argentina), it's likely decimal.
                v = v.replace(',', '.')
            elif '.' in v:
                # Only dot present: could be decimal (US) or thousands (ES).
                # Check if there are multiple dots
                if v.count('.') > 1:
                    v = v.replace('.', '')
                else:
                    # Single dot: if it's followed by 3 digits at the end, it's likely thousands
                    if re.search(r'\.\d{3}$', v):
                        v = v.replace('.', '')
                    # Otherwise keep as decimal
            
            try:
                return float(v)
            except ValueError:
                return None
        return v

    @field_validator("cantidad_dormitorios", "cantidad_banos", "cantidad_ambientes", mode="before")
    @classmethod
    def standardize_int(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True) or v is None:
            return v
        if isinstance(v, str):
            match = re.search(r'(\d+)', v)
            if match:
                return int(match.group(1))
            return None
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return None

    @field_validator("tiene_patio", "tiene_quincho", "tiene_pileta", "tiene_cochera", 
                     "tiene_balcon", "tiene_terraza", mode="before")
    @classmethod
    def standardize_bool(cls, v, info):
        if not config.STANDARDIZATION_CONFIG.get(info.field_name, True) or v is None:
            return v
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ['true', 'si', 'sí', 'yes', '1', 't']
        if isinstance(v, (int, float)):
            return bool(v)
        return False

def standardize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for standardizing property data.
    """
    if not config.STANDARDIZATION_ENABLED:
        return data
        
    try:
        # Create standardizer and export back to dict
        standardizer = PropertyStandardizer(**data)
        standardized_data = standardizer.model_dump(exclude_unset=True)
        
        # Merge back with original data to preserve fields not in standardizer (like url, descripcion_breve)
        result = {**data, **standardized_data}
        
        # Add logging for changes
        for key, val in standardized_data.items():
            if key in data and data[key] != val:
                logger.info(f"Standardized field '{key}': '{data[key]}' -> '{val}'")
                
        return result
    except Exception as e:
        logger.error(f"Error during standardization: {e}")
        return data  # Return original data on failure

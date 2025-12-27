"""
LLM processor module for extracting structured data from property listings.
Supports both Ollama (local) and Google Gemini (API).
Now uses hybrid extraction: structured data + LLM for complex fields.
"""

import json
import requests
import logging
from typing import Dict, Any
from src.utils import config
from src.core.structured_extractor import StructuredExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProcessor:
    """Process raw property data using hybrid extraction: structured + LLM."""
    
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.structured_extractor = StructuredExtractor()
        logger.info(f"Initialized LLM processor with provider: {self.provider}")
    
    def create_extraction_prompt(self, text: str, url: str, already_extracted: Dict[str, Any], missing_fields: list) -> str:
        """Create a prompt for the LLM to extract only missing property data."""
        fields_json = json.dumps(missing_fields, indent=2, ensure_ascii=False)
        extracted_json = json.dumps(already_extracted, indent=2, ensure_ascii=False)
        
        prompt = f"""Eres un asistente experto en extraer información de listados de propiedades inmobiliarias.

A continuación se te proporciona el texto de una página web de una propiedad.

URL: {url}

DATOS YA EXTRAÍDOS (NO NECESITAS EXTRAER ESTOS):
{extracted_json}

TEXTO DE LA PROPIEDAD:
{text[:10000]}

Tu tarea es extraer ÚNICAMENTE la siguiente información que aún falta:

Campos a extraer:
{fields_json}

INSTRUCCIONES IMPORTANTES:
1. Devuelve ÚNICAMENTE un objeto JSON válido, sin texto adicional antes ni después.
2. Extrae SOLO los campos listados arriba que faltan. NO repitas los campos ya extraídos.
3. Para campos booleanos (tiene_patio, tiene_quincho, tiene_pileta, tiene_cochera), usa true/false.
4. Para campos numéricos, usa números sin comas ni puntos como separadores de miles.
5. Si no encuentras información para un campo, usa null.
6. Para "descripcion_breve", extrae un resumen de máximo 200 caracteres.
7. Sé preciso y busca la información exacta en el texto.

EJEMPLO DE FORMATO DE RESPUESTA (solo los campos faltantes):
{{
  "barrio": "Alberdi",
  "direccion": "Cerrito 1700",
  "tiene_patio": true,
  "tiene_quincho": true,
  "tiene_pileta": false,
  "tiene_cochera": false,
  "antiguedad": "15 años",
  "descripcion_breve": "Casa reciclada con patio y quincho"
}}

Ahora extrae SOLO los campos faltantes de la propiedad:"""
        
        return prompt
    
    def call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            url = f"{config.OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent extraction
                }
            }
            
            logger.info(f"Calling Ollama at {url} with model {config.OLLAMA_MODEL}")
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Failed to call Ollama: {e}")
    
    def call_google(self, prompt: str) -> str:
        """Call Google Gemini API (future implementation)."""
        # TODO: Implement when user needs it
        raise NotImplementedError("Google Gemini integration not yet implemented")
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling common formatting issues.
        """
        # Try to find JSON in the response
        response = response.strip()
        
        # Find the first { and last }
        start = response.find('{')
        end = response.rfind('}')
        
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in response")
        
        json_str = response[start:end+1]
        
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Response was: {json_str[:500]}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")
    
    def validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted data before saving to database.
        Ensures data types are correct and values are within acceptable ranges.
        """
        cleaned = {}
        
        for field_name in config.EXTRACTION_FIELDS: # Renamed 'field' to 'field_name' for clarity as per instruction
            value = data.get(field_name)
            
            # Handle numeric fields
            if field_name in ["metros_cuadrados_cubiertos", "metros_cuadrados_totales"]:
                # Square meters: REAL with 2 decimal places
                if value is not None:
                    try:
                        if isinstance(value, (int, float)):
                            num_value = float(value)
                        else:
                            v_str = str(value).strip().replace(',', '.')
                            num_value = float(v_str) if v_str else None
                        
                        # Standardize to 2 decimal places
                        cleaned[field_name] = round(num_value, 2) if num_value is not None else None
                    except (ValueError, TypeError):
                        cleaned[field_name] = None
                else:
                    cleaned[field_name] = None
            
            elif field_name in ["precio", "cantidad_dormitorios", "cantidad_banos", "cantidad_ambientes"]:
                # Other numeric fields
                if value is not None:
                    try:
                        # If it's already a number, keep it as is (will be cast below)
                        if isinstance(value, (int, float)):
                            num_value = float(value)
                        else:
                            # It's a string, clean basic whitespace
                            v_str = str(value).strip()
                            if not v_str:
                                num_value = None
                            else:
                                # Don't remove separators here yet, let the standardizer handle complex formats
                                # Only handle the simplest case if it's already a clean number string
                                try:
                                    num_value = float(v_str)
                                except ValueError:
                                    # If not a clean number string, pass through as string for the standardizer to handle
                                    num_value = v_str
                        
                        # Apply specific types
                        if field_name == "precio":
                            cleaned[field_name] = float(num_value) if isinstance(num_value, (int, float)) else num_value
                        else:
                            cleaned[field_name] = int(float(num_value)) if isinstance(num_value, (int, float)) else num_value
                            
                    except (ValueError, TypeError):
                        cleaned[field_name] = value # Pass through for standardizer
                else:
                    cleaned[field_name] = None
            
            # Handle boolean fields
            elif field_name in ["tiene_patio", "tiene_quincho", "tiene_pileta", "tiene_cochera",
                          "tiene_balcon", "tiene_terraza"]:
                if isinstance(value, bool):
                    cleaned[field_name] = value
                elif isinstance(value, str):
                    cleaned[field_name] = value.lower() in ['true', 'sí', 'si', 'yes', '1']
                else:
                    cleaned[field_name] = False
            
            # Handle string fields
            else:
                if value is not None:
                    cleaned[field_name] = str(value).strip()
                    # Limit string length
                    if field_name == "descripcion_breve":
                        cleaned[field_name] = cleaned[field_name][:200]
                    elif field_name not in ["direccion", "barrio", "tipo_operacion", "moneda", "antiguedad", "piso", 
                                      "tipo_inmueble", "orientacion"]:
                        cleaned[field_name] = cleaned[field_name][:500]
                else:
                    cleaned[field_name] = None
        
        return cleaned
    
    def process_property(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to process scraped property data using hybrid extraction.
        1. First uses structured extraction for accurate numerical/simple fields
        2. Then uses LLM only for complex/missing fields
        Returns structured and validated data ready for database insertion.
        """
        url = scraped_data['url']
        text = scraped_data['text']
        html = scraped_data['html']
        
        logger.info(f"Processing property with HYBRID extraction: {url}")
        
        # Step 1: Structured extraction
        structured_result = self.structured_extractor.extract_structured_data(url, html, text)
        already_extracted = structured_result['extracted']
        missing_fields = []
        
        # Determine which fields still need to be extracted
        for field in config.EXTRACTION_FIELDS:
            if field not in already_extracted:
                missing_fields.append(field)
        
        logger.info(f"Structured extraction: {len(already_extracted)} fields extracted")
        logger.info(f"LLM needed for: {len(missing_fields)} fields")
        
        # Step 2: LLM extraction for missing fields (if any)
        llm_extracted = {}
        if missing_fields:
            # Create prompt for missing fields only
            prompt = self.create_extraction_prompt(text, url, already_extracted, missing_fields)
            
            # Call LLM
            if self.provider == "ollama":
                response = self.call_ollama(prompt)
            elif self.provider == "google":
                response = self.call_google(prompt)
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
            
            logger.info(f"LLM response received (length: {len(response)} chars)")
            
            # Parse JSON from LLM response
            try:
                llm_extracted = self.parse_json_response(response)
            except Exception as e:
                logger.warning(f"Failed to parse LLM response, using empty dict: {e}")
                llm_extracted = {}
        
        # Step 3: Merge structured and LLM-extracted data
        merged_data = {**already_extracted, **llm_extracted}
        
        # Step 4: Validate and clean
        cleaned_data = self.validate_and_clean_data(merged_data)
        
        # Add URL to the data
        cleaned_data['url'] = url
        
        return cleaned_data


def test_llm_processor():
    """Test the LLM processor with sample text."""
    processor = LLMProcessor()
    
    sample_text = """
    Casa en Venta - Rosario, Barrio Alberdi
    Precio: USD 180.000
    3 dormitorios | 2 baños | 120 m² cubiertos | 200 m² totales
    
    Hermosa casa reciclada con patio y quincho. Cuenta con cochera para 2 autos.
    Excelente ubicación en barrio residencial.
    
    Características:
    - Patio amplio
    - Quincho con parrilla
    - Cochera
    - Antigüedad: 15 años
    """
    
    scraped_data = {
        'url': 'https://example.com/test',
        'text': sample_text,
        'html': ''
    }
    
    try:
        result = processor.process_property(scraped_data)
        print("\nExtracted data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_llm_processor()

"""
Módulo para calcular campos derivados/calculados a partir de datos extraídos.
Los campos calculados se agregan después del procesamiento LLM pero antes de guardar en DB.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def calculate_costo_metro_cuadrado(data: Dict[str, Any]) -> Optional[float]:
    """
    Calcula el costo por metro cuadrado ponderado.
    
    Fórmula: precio / ((m2_totales - m2_cubiertos) * 0.25 + m2_cubiertos)
    
    Esta fórmula pondera:
    - 100% los metros cubiertos
    - 25% los metros descubiertos (patio, terraza, balcón, etc.)
    
    Args:
        data: Diccionario con los datos de la propiedad
        
    Returns:
        Costo por m² ponderado, o None si faltan datos
    """
    try:
        precio = data.get('precio')
        m2_totales = data.get('metros_cuadrados_totales')
        m2_cubiertos = data.get('metros_cuadrados_cubiertos')
        
        # Validar que tengamos todos los datos necesarios
        if precio is None or m2_totales is None or m2_cubiertos is None:
            logger.debug("Faltan datos para calcular costo_metro_cuadrado")
            return None
        
        # Convertir a números si vienen como strings
        precio = float(precio)
        m2_totales = float(m2_totales)
        m2_cubiertos = float(m2_cubiertos)
        
        # Evitar división por cero y valores negativos
        if m2_totales <= 0 or m2_cubiertos <= 0 or precio <= 0:
            logger.warning(f"Valores inválidos: precio={precio}, m2_totales={m2_totales}, m2_cubiertos={m2_cubiertos}")
            return None
        
        # Validar que m2_cubiertos no sea mayor que m2_totales
        if m2_cubiertos > m2_totales:
            logger.warning(f"m2_cubiertos ({m2_cubiertos}) > m2_totales ({m2_totales}), usando m2_totales")
            m2_cubiertos = m2_totales
        
        # Calcular metros descubiertos
        m2_descubiertos = m2_totales - m2_cubiertos
        
        # Aplicar fórmula: precio / (m2_descubiertos * 0.25 + m2_cubiertos)
        m2_ponderados = (m2_descubiertos * 0.25) + m2_cubiertos
        
        if m2_ponderados <= 0:
            return None
        
        costo_m2 = precio / m2_ponderados
        
        logger.debug(f"Calculado costo_m2: {costo_m2:.2f} (precio={precio}, m2_ponderados={m2_ponderados:.2f})")
        
        return round(costo_m2, 2)
    
    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.error(f"Error calculando costo_metro_cuadrado: {e}")
        return None


def calculate_all_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula todos los campos derivados y los agrega al diccionario de datos.
    
    Esta función es el punto de entrada principal para calcular campos.
    Agrega nuevos campos al diccionario sin modificar los existentes.
    
    Args:
        data: Diccionario con los datos extraídos de la propiedad
        
    Returns:
        Mismo diccionario con campos calculados agregados
    """
    # Calcular costo por metro cuadrado
    costo_m2 = calculate_costo_metro_cuadrado(data)
    if costo_m2 is not None:
        data['costo_metro_cuadrado'] = costo_m2
        logger.info(f"  ✓ costo_metro_cuadrado: {costo_m2:.2f}")
    else:
        data['costo_metro_cuadrado'] = None
        logger.debug("  ✗ costo_metro_cuadrado: No se pudo calcular")
    
    # AQUÍ SE PUEDEN AGREGAR MÁS CAMPOS CALCULADOS EN EL FUTURO:
    # 
    # Ejemplos de campos calculados futuros:
    # - precio_por_ambiente = precio / cantidad_ambientes
    # - precio_por_dormitorio = precio / cantidad_dormitorios
    # - ratio_cubierto_total = m2_cubiertos / m2_totales
    # - puntaje_caracteristicas = suma de booleanos (patio, quincho, etc.)
    # 
    # data['precio_por_ambiente'] = calculate_precio_por_ambiente(data)
    # data['ratio_cubierto_total'] = calculate_ratio_cubierto_total(data)
    
    return data

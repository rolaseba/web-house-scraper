#!/usr/bin/env python3
"""Script to view property database contents in a readable format."""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import PropertyDatabase

def format_currency(precio, moneda):
    """Format price with currency."""
    if precio:
        return f"{moneda} ${precio:,.0f}"
    return "N/A"

def format_features(prop):
    """Format property features into a readable list."""
    features = []
    if prop.get('tiene_patio'): features.append('Patio')
    if prop.get('tiene_quincho'): features.append('Quincho')
    if prop.get('tiene_pileta'): features.append('Pileta')
    if prop.get('tiene_cochera'): features.append('Cochera')
    if prop.get('tiene_balcon'): features.append('Balcón')
    if prop.get('tiene_terraza'): features.append('Terraza')
    return ', '.join(features) if features else 'Ninguna especial'

def truncate_url(url, max_len=80):
    """Truncate URL for display."""
    if len(url) > max_len:
        return url[:max_len] + '...'
    return url

def main():
    with PropertyDatabase() as db:
        properties = db.get_all_properties()
        
        print("\n" + "="*100)
        print("🏠 PROPIEDADES EN LA BASE DE DATOS")
        print("="*100)
        
        for i, prop in enumerate(properties, 1):
            print(f"\n{i}. {prop.get('tipo_operacion', 'N/A').upper()} - {prop.get('barrio', 'N/A')}")
            
            # Type and address
            tipo = prop.get('tipo_inmueble', 'N/A')
            if tipo and tipo != 'N/A':
                print(f"   🏢 Tipo: {tipo}")
            print(f"   📍 Dirección: {prop.get('direccion', 'N/A')}")
            
            # Price
            precio_str = format_currency(prop.get('precio'), prop.get('moneda', 'USD'))
            costo_m2 = prop.get('costo_metro_cuadrado')
            if costo_m2:
                precio_str += f" | {costo_m2:.2f} {prop.get('moneda', 'USD')}/m²"
            print(f"   💰 Precio: {precio_str}")
            
            # Surface
            m2_cub = prop.get('metros_cuadrados_cubiertos') or 'N/A'
            m2_tot = prop.get('metros_cuadrados_totales') or 'N/A'
            print(f"   📏 {m2_cub} m² cubiertos | {m2_tot} m² totales")
            
            # Rooms
            dorms = prop.get('cantidad_dormitorios') or 'N/A'
            banos = prop.get('cantidad_banos') or 'N/A'
            ambientes = prop.get('cantidad_ambientes')
            rooms_str = f"   🛏️  {dorms} dormitorios | {banos} baños"
            if ambientes:
                rooms_str += f" | {ambientes} ambientes"
            print(rooms_str)
            
            # Floor and orientation
            details = []
            piso = prop.get('piso')
            if piso and piso not in ['0', 'N/A', None]:
                details.append(f"Piso {piso}")
            
            orientacion = prop.get('orientacion')
            if orientacion and orientacion != 'N/A':
                details.append(f"Orientación {orientacion}")
            
            antiguedad = prop.get('antiguedad')
            if antiguedad and antiguedad != 'N/A':
                details.append(f"{antiguedad}")
            
            if details:
                print(f"   🏗️  {' | '.join(details)}")
            
            # Features
            features = format_features(prop)
            if features != 'Ninguna especial':
                print(f"   ✨ Características: {features}")
            
            # Description
            desc = prop.get('descripcion_breve', 'N/A')
            print(f"   📝 {desc}")
            
            # URL
            print(f"   🔗 {truncate_url(prop.get('url', 'N/A'))}")
            print("-" * 100)
        
        print(f"\nTotal: {len(properties)} propiedades")
        print("="*100 + "\n")

if __name__ == "__main__":
    main()

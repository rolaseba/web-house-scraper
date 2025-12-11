"""
Utilities for viewing database content.
"""
from src.database.database import PropertyDatabase
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

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

def show_stats():
    """Show database statistics."""
    with PropertyDatabase() as db:
        count = db.count_properties()
        status_counts = db.get_status_counts()
        
        table = Table(title="[bold]DATABASE STATISTICS[/bold]", box=box.ROUNDED, border_style="cyan")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="bold")
        
        table.add_row("Total Properties", str(count))
        table.add_row("", "")
        
        # Status breakdown
        if status_counts:
            table.add_row("[bold]Status Breakdown:[/bold]", "")
            for status, cnt in status_counts.items():
                percent = (cnt / count * 100) if count > 0 else 0
                status_label = "Not reviewed" if status == 'blank' else status
                table.add_row(f"  {status_label}", f"{cnt} ({percent:.1f}%)")
            table.add_row("", "")
        
        table.add_row("Database File", db.db_file)
        
        console.print()
        console.print(table)
        console.print()

def view_database(status: str = None):
    """View properties in the database, optionally filtered by status."""
    with PropertyDatabase() as db:
        # Get properties based on filter
        if status:
            properties = db.get_properties_by_status(status)
            filter_text = f" (Status: {status})"
        else:
            properties = db.get_all_properties()
            filter_text = ""
        
        print("\n" + "="*100)
        print(f"🏠 PROPIEDADES EN LA BASE DE DATOS{filter_text}")
        print("="*100)
        
        if not properties:
            print(f"\nNo properties found{' with status ' + status if status else ''}")
            print("="*100 + "\n")
            return
        
        for i, prop in enumerate(properties, 1):
            # Status badge
            prop_status = prop.get('status', '')
            status_badge = ""
            if prop_status:
                if prop_status == 'YES':
                    status_badge = " ✅"
                elif prop_status == 'NO':
                    status_badge = " ❌"
                elif prop_status == 'MAYBE':
                    status_badge = " 🤔"
            else:
                status_badge = " ⬜"  # Not reviewed
            
            print(f"\n{i}. {status_badge} {prop.get('tipo_operacion', 'N/A').upper()} - {prop.get('barrio', 'N/A')}")
            
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

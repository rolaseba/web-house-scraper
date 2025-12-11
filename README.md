# Web House Scraper

Aplicación para scrapear propiedades inmobiliarias de Argenprop y Zonaprop, procesar la información con un **sistema híbrido** (extracción estructurada + LLM local) y guardarla en una base de datos SQLite.

## Características

- 🔍 Scraping de propiedades desde Argenprop y Zonaprop
- 🎯 **Sistema Híbrido de Extracción**:
  - Extracción estructurada con regex/CSS para campos numéricos (100% precisión)
  - LLM (Ollama) solo para campos complejos (direcciones, descripciones)
- ⚙️ **Configuración por Sitio**: Patrones definidos en `data/site_configs.json` (sin modificar código)
- 🤖 Procesamiento inteligente con LLM (Ollama o Google Gemini)
- 💾 Almacenamiento en SQLite con funcionalidad **UPSERT** (insert/update)
- 🛡️ Manejo de anti-scraping mediante Playwright
- 📦 **Estructura Profesional**: Organizado según mejores prácticas de Python

## Requisitos

- Python 3.8+
- Ollama instalado y corriendo localmente (por defecto)
- Sistema operativo: Linux, macOS, Windows

## Instalación

1. **Clonar el repositorio**

```bash
cd /home/seba/Documentos/Data\ Science\ Projects/web-house-scraper
```

2. **Crear entorno virtual**

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env si es necesario
```

5. **Asegurar que Ollama esté corriendo**

```bash
ollama serve  # En otra terminal
ollama pull deepseek-r1:latest  # Descargar el modelo
```

## Estructura del Proyecto

```
web-house-scraper/
│
├── 📁 src/                          # Código fuente
│   ├── 📁 core/                     # Lógica principal
│   │   ├── scraper.py              # Web scraping
│   │   ├── llm_processor.py        # Procesamiento híbrido LLM
│   │   └── structured_extractor.py # Extracción estructurada
│   │
│   ├── 📁 database/                 # Capa de datos
│   │   └── database.py             # SQLite con UPSERT
│   │
│   └── 📁 utils/                    # Utilidades
│       └── config.py               # Configuración central
│
├── 📁 data/                         # Datos y configuraciones
│   ├── properties.db               # Base de datos SQLite
│   ├── links-to-scrap.md          # URLs a procesar
│   └── site_configs.json          # Patrones de extracción por sitio
│
├── 📁 scripts/                      # Scripts ejecutables
│   ├── main.py                     # Script principal
│   └── view_db.py                  # Visualizar base de datos
│
├── 📁 tests/                        # Tests (preparado para el futuro)
│
├── .env                             # Variables de entorno (privado)
├── .env.example                     # Ejemplo de configuración
├── requirements.txt                 # Dependencias Python
└── README.md                        # Esta documentación
```

## Uso Rápido

### 1. Agregar URLs

Edita `data/links-to-scrap.md` y agrega URLs (una por línea):

```
https://www.zonaprop.com.ar/propiedades/...
https://www.argenprop.com/departamento-en-venta...
```

### 2. Ejecutar el scraper

```bash
python scripts/main.py
```

### 3. Ver resultados

```bash
python scripts/view_db.py
```

O acceder directamente a la base de datos:

```bash
sqlite3 data/properties.db "SELECT * FROM properties;"
```

## Configuración

### Campos Extraídos

El sistema extrae **21 campos** automáticamente (definidos en `src/utils/config.py`):

**Básicos:**
- `tipo_operacion` (venta/alquiler)
- `tipo_inmueble` (casa/departamento)
- `direccion`
- `barrio`

**Medidas:**
- `metros_cuadrados_cubiertos`
- `metros_cuadrados_totales`
- `precio`
- `moneda` (USD/ARS)

**Distribución:**
- `cantidad_dormitorios`
- `cantidad_banos`
- `cantidad_ambientes`

**Características booleanas:**
- `tiene_patio`
- `tiene_quincho`
- `tiene_pileta`
- `tiene_cochera`
- `tiene_balcon`
- `tiene_terraza`

**Detalles adicionales:**
- `piso` (PB, 1, 2, 3... o 0 para casas)
- `orientacion` (Norte, Sur, Este, Oeste)
- `antiguedad`
- `descripcion_breve`

### Variables de Entorno (.env)

```bash
LLM_PROVIDER=ollama                      # ollama o google
OLLAMA_MODEL=deepseek-r1:latest         # Modelo de Ollama
OLLAMA_BASE_URL=http://localhost:11434  # URL base de Ollama
GOOGLE_API_KEY=                         # Para usar Gemini (opcional)
GEMINI_MODEL=gemini-pro                 # Modelo de Gemini
```

## Sistema Híbrido de Extracción

La aplicación usa un enfoque de **dos pasos** para máxima precisión y eficiencia:

### Paso 1: Extracción Estructurada

Primero extrae campos usando **patrones regex/CSS** definidos en `data/site_configs.json`:

✅ **100% precisión** en:
- Precio
- Moneda  
- Metros cuadrados (cubiertos y totales)
- Cantidad de dormitorios/baños
- Tipo de operación (venta/alquiler)

### Paso 2: Procesamiento LLM

Luego usa el **LLM solo para campos complejos**:
- Dirección completa
- Barrio/zona
- Características (patio, quincho, pileta, balcón, terraza, etc.)
- Tipo de inmueble
- Orientación
- Piso
- Descripción breve
- Antigüedad

### Ventajas

- ⚡ **100% precisión** en campos numéricos
- 🚀 **Más rápido**: LLM procesa solo ~40% de los campos
- 🔧 **Mantenible**: Patrones en JSON, no en código
- 📈 **Escalable**: Fácil agregar nuevos sitios

### Agregar Nuevo Sitio

Edita `data/site_configs.json` y agrega configuración:

```json
{
  "nuevositio.com": {
    "name": "Nuevo Sitio",
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

## Funcionalidad UPSERT

El sistema implementa **UPSERT** (Update or Insert) automático:

### Comportamiento

Cuando ejecutas la app con un link que ya existe en la base de datos:

- ✅ **Se actualiza** la propiedad con los nuevos datos extraídos
- ✅ **Se actualiza** el timestamp `scraped_at` automáticamente  
- ✅ El terminal muestra claramente: `🔄 Updated property`
- ✅ El resumen final distingue entre "New properties" y "Updated properties"

### Ejemplo de Output

```
[1/5] Processing: https://www.zonaprop.com.ar/...
INFO:src.database.database:🔄 Updated property: https://www.zonaprop.com.ar/...
INFO:__main__:✓ Successfully updated existing property

SUMMARY
================================================================================
Total URLs:           5
New properties:       0
Updated properties:   5    👈 Todas actualizadas
Failed:               0
```

### Casos de Uso

- 📊 Actualizar precios que cambian
- 🔄 Refrescar características modificadas
- 📈 Hacer seguimiento temporal de propiedades
- 🔍 Monitoreo continuo del mercado

## Solución de Problemas

### Error: "externally-managed-environment"

**Solución**: Usar entorno virtual (ver instalación).

### Error: "Links file not found"

**Causa**: Archivo `data/links-to-scrap.md` no existe o está vacío.

**Solución**: 
```bash
echo "https://www.zonaprop.com.ar/..." > data/links-to-scrap.md
```

### Timeout en scraping

**Causa**: Algunas páginas pueden tardar en cargar.

**Solución**: Ajustar timeout en `src/core/scraper.py` (línea ~40).

### LLM no responde

**Verificar que Ollama esté corriendo**:
```bash
ollama list  # Ver modelos instalados
ollama serve # Iniciar servidor
```

### Error 403 Forbidden

**Normal**: Zonaprop usa protección anti-scraping.

**Solución automática**: El sistema usa Playwright como fallback (ya implementado).

## Notas Importantes

- 🔒 **Anti-scraping**: Zonaprop usa protección 403 → Se resuelve automáticamente con Playwright
- 🤖 **LLM Local**: Asegúrate de que Ollama esté corriendo: `ollama serve`
- 📦 **Modelo**: Por defecto usa `deepseek-r1:latest` → Descárgalo con: `ollama pull deepseek-r1:latest`
- 💰 **APIs Pagas**: Para usar Google Gemini, configura `GOOGLE_API_KEY` en `.env`
- 🔄 **UPSERT**: Re-ejecutar con los mismos links **actualiza** los datos automáticamente
- 📁 **Estructura**: Proyecto organizado según Python best practices (src/, data/, scripts/)

## Ejemplos de Ejecución

### Activar entorno y ejecutar

```bash
cd /home/seba/Documentos/Data\ Science\ Projects/web-house-scraper
source venv/bin/activate
python scripts/main.py
```

### Ver propiedades formateadas

```bash
python scripts/view_db.py
```

### Consulta SQL directa

```bash
sqlite3 data/properties.db
> SELECT direccion, precio, moneda, cantidad_dormitorios FROM properties;
> .quit
```

## Contribuir

Para contribuir al proyecto:

1. Crear feature branch
2. Agregar tests en `tests/`
3. Actualizar documentación si es necesario
4. Enviar pull request

## Licencia

MIT

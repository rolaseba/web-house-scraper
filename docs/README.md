# PropertyAnalyzer - Analizador de Propiedades Inmobiliarias

Una aplicación web profesional para visualizar, filtrar y comparar propiedades inmobiliarias. Compatible con GitHub Pages y diseñada para análisis detallado de propiedades.

## Características Principales

### 🏠 Visualización de Propiedades
- Tabla interactiva con todas las propiedades
- Filtros avanzados por tipo, precio, ubicación y características
- Búsqueda en tiempo real
- Paginación inteligente

### 📊 Comparación de Propiedades
- Selección múltiple de propiedades
- Comparación detallada lado a lado
- Gráficos interactivos de precios y características
- Análisis automático de diferencias

### 🎨 Diseño Moderno
- Interfaz responsive y profesional
- Animaciones suaves con Anime.js
- Fondo animado con p5.js
- Efectos visuales con múltiples librerías

### 📈 Análisis y Reportes
- Estadísticas en tiempo real
- Gráficos de comparación con ECharts.js
- Exportación de datos filtrados
- Recomendaciones inteligentes

## Tecnologías Utilizadas

### Frontend
- **HTML5** - Estructura semántica
- **Tailwind CSS** - Framework de estilos
- **JavaScript ES6+** - Lógica de aplicación

### Librerías de Animación y Visualización
- **Anime.js** - Animaciones de interfaz
- **ECharts.js** - Gráficos interactivos
- **p5.js** - Fondo animado con partículas
- **Matter.js** - Física de partículas
- **Pixi.js** - Efectos visuales
- **Splide.js** - Carruseles (preparado para futuras versiones)

## Estructura del Proyecto

```
PropertyAnalyzer/
├── index.html              # Página principal con tabla de propiedades
├── comparison.html         # Página de comparación detallada
├── main.js                 # JavaScript principal
├── comparison.js           # JavaScript de comparación
├── properties_export.csv   # Base de datos de propiedades
└── README.md              # Este archivo
```

## Instalación y Uso

### Opción 1: GitHub Pages (Recomendado)
1. Fork este repositorio
2. Activa GitHub Pages en Settings > Pages
3. Selecciona la rama y carpeta deseadas
4. Tu aplicación estará disponible en `username.github.io/PropertyAnalyzer`

### Opción 2: Local
1. Clona el repositorio
2. Abre `index.html` en tu navegador
3. O usa un servidor web local:
   ```bash
   python -m http.server 8000
   ```

## Actualización de Datos

La aplicación está diseñada para trabajar con archivos CSV. Para actualizar los datos:

1. Reemplaza el archivo `properties_export.csv` con tus nuevos datos
2. Asegúrate de mantener la misma estructura de columnas
3. La aplicación cargará automáticamente los nuevos datos

### Estructura del CSV
El archivo CSV debe contener las siguientes columnas:
- `id` - Identificador único
- `url` - Enlace a la propiedad
- `tipo_operacion` - venta/alquiler
- `tipo_inmueble` - casa/departamento/local
- `direccion` - Dirección completa
- `barrio` - Barrio o zona
- `metros_cuadrados_cubiertos` - Superficie cubierta
- `metros_cuadrados_totales` - Superficie total
- `precio` - Precio en USD
- `moneda` - Tipo de moneda
- `cantidad_dormitorios` - Número de dormitorios
- `cantidad_banos` - Número de baños
- `cantidad_ambientes` - Número de ambientes
- `tiene_patio` - 1/0 (sí/no)
- `tiene_quincho` - 1/0 (sí/no)
- `tiene_pileta` - 1/0 (sí/no)
- `tiene_cochera` - 1/0 (sí/no)
- `tiene_balcon` - 1/0 (sí/no)
- `tiene_terraza` - 1/0 (sí/no)
- `piso` - Número de piso (si aplica)
- `orientacion` - Orientación (Norte/Sur/Este/Oeste)
- `antiguedad` - Años o "nueva"
- `descripcion_breve` - Descripción corta
- `costo_metro_cuadrado` - Precio por m²
- `scraped_at` - Fecha de obtención
- `status` - Estado (YES/NO/MAYBE)

## Funcionalidades Detalladas

### Filtros Disponibles
- **Búsqueda por texto**: Dirección, barrio o descripción
- **Tipo de operación**: Venta o Alquiler
- **Tipo de inmueble**: Casa, Departamento o Local
- **Rango de precio**: Mínimo y máximo en USD
- **Dormitorios**: 1, 2, 3 o 4+

### Comparación de Propiedades
- Selección de hasta 3 propiedades simultáneamente
- Comparación lado a lado de todas las características
- Gráficos interactivos de:
  - Precios comparados
  - Superficie cubierta vs total
  - Características adicionales
  - Costo por metro cuadrado
- Análisis automático de diferencias
- Recomendaciones basadas en métricas

### Exportación de Datos
- Exportación de propiedades filtradas a CSV
- Exportación de comparación detallada
- Datos listos para análisis en Excel o Google Sheets

## Personalización

### Colores y Estilos
El proyecto utiliza Tailwind CSS con una paleta de colores personalizada:
- **Azul primario**: #2563eb
- **Verde éxito**: #059669
- **Gris neutro**: #64748b
- **Rojo alerta**: #dc2626

Para cambiar los colores, modifica las clases CSS en los archivos HTML o actualiza la configuración de Tailwind.

### Animaciones
Las animaciones están configuradas en `main.js` y `comparison.js`. Puedes:
- Ajustar duraciones y easing
- Agregar nuevas animaciones
- Modificar efectos de hover y transiciones

## Futuras Mejoras Planificadas

- [ ] Integración con Google Maps para ubicaciones
- [ ] Galería de imágenes con Splide.js
- [ ] Modo oscuro
- [ ] Filtros avanzados (antigüedad, orientación)
- [ ] Guardado de comparaciones
- [ ] Generación de reportes PDF
- [ ] Filtros combinados con lógica AND/OR
- [ ] Vista de mapa con marcadores

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## Contacto

Para preguntas o soporte, por favor abre un issue en el repositorio.

---

**PropertyAnalyzer** - Analiza propiedades como un profesional 🏡📊
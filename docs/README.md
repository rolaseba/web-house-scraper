# PropertyAnalyzer - Real Estate Property Analyzer

A professional web application to visualize, filter, and compare real estate properties. Compatible with GitHub Pages and designed for detailed property analysis.

## Main Features

### 🏠 Property Visualization
- Interactive table with all properties
- Advanced filters by type, price, location, and characteristics
- Real-time search
- Smart pagination

### 📊 Property Comparison
- Multiple property selection
- Detailed side-by-side comparison
- Interactive charts for prices and characteristics
- Automatic difference analysis

### 🎨 Modern Design
- Responsive and professional interface
- Smooth animations with Anime.js
- Animated background with p5.js
- Visual effects with multiple libraries

### 📈 Analysis and Reports
- Real-time statistics
- Comparison charts with ECharts.js
- Filtered data export
- Smart recommendations

## Technologies Used

### Frontend
- **HTML5** - Semantic structure
- **Tailwind CSS** - Styling framework
- **JavaScript ES6+** - Application logic

### Animation and Visualization Libraries
- **Anime.js** - Interface animations
- **ECharts.js** - Interactive charts
- **p5.js** - Animated background with particles
- **Matter.js** - Particle physics
- **Pixi.js** - Visual effects
- **Splide.js** - Carousels (prepared for future versions)

## Project Structure

```
PropertyAnalyzer/
├── index.html              # Main page with property table
├── comparison.html         # Detailed comparison page
├── main.js                 # Main JavaScript
├── comparison.js           # Comparison JavaScript
├── properties_export.csv   # Property database
└── README.md               # This file
```

## Installation and Usage

### Option 1: GitHub Pages (Recommended)
1. Fork this repository
2. Activate GitHub Pages in Settings > Pages
3. Select the desired branch and folder
4. Your application will be available at `username.github.io/PropertyAnalyzer`

### Option 2: Local
1. Clone the repository
2. Open `index.html` in your browser
3. Or use a local web server:

   **Option A: Automatic Script (Recommended)**
   ```bash
   # From the project root
   ./scripts/serve_docs.sh
   ```

   **Option B: Manual**
   ```bash
   cd docs
   python -m http.server 8000
   ```
   Then open `http://localhost:8000`

## Data Update

The application is designed to work with CSV files. To update the data:

1. Replace the `properties_export.csv` file with your new data
2. Ensure you keep the same column structure
3. The application will automatically load the new data

### CSV Structure
The CSV file must contain the following columns:
- `id` - Unique identifier
- `url` - Link to the property
- `tipo_operacion` - sale/rent
- `tipo_inmueble` - house/apartment/commercial
- `direccion` - Full address
- `barrio` - Neighborhood or zone
- `metros_cuadrados_cubiertos` - Covered surface area
- `metros_cuadrados_totales` - Total surface area
- `precio` - Price in USD
- `moneda` - Currency type
- `cantidad_dormitorios` - Number of bedrooms
- `cantidad_banos` - Number of bathrooms
- `cantidad_ambientes` - Number of rooms
- `tiene_patio` - 1/0 (yes/no)
- `tiene_quincho` - 1/0 (yes/no)
- `tiene_pileta` - 1/0 (yes/no)
- `tiene_cochera` - 1/0 (yes/no)
- `tiene_balcon` - 1/0 (yes/no)
- `tiene_terraza` - 1/0 (yes/no)
- `piso` - Floor number (if applicable)
- `orientacion` - Orientation (North/South/East/West)
- `antiguedad` - Years or "new"
- `descripcion_breve` - Short description
- `costo_metro_cuadrado` - Price per m²
- `scraped_at` - Retrieval date
- `status` - Status (YES/NO/MAYBE)

## Detailed Features

### Available Filters
- **Text Search**: Address, neighborhood, or description
- **Operation Type**: Sale or Rent (*Venta* / *Alquiler*)
- **Property Type**: House, Apartment, or Commercial (*Casa*, *Departamento*, *Local*)
- **Price Range**: Minimum and maximum in USD
- **Bedrooms**: 1, 2, 3, or 4+

### Property Comparison
- Selection of up to 3 properties simultaneously
- Side-by-side comparison of all characteristics
- Interactive charts of:
  - Compared prices
  - Covered vs total surface area
  - Additional features
  - Cost per square meter
- Automatic difference analysis
- Recommendations based on metrics

### Data Export
- Export filtered properties to CSV
- Export detailed comparison
- Data ready for analysis in Excel or Google Sheets

## Customization

### Colors and Styles
The project uses Tailwind CSS with a custom color palette:
- **Primary Blue**: #2563eb
- **Success Green**: #059669
- **Neutral Gray**: #64748b
- **Alert Red**: #dc2626

To change colors, modify the CSS classes in the HTML files or update the Tailwind configuration.

### Animations
Animations are configured in `main.js` and `comparison.js`. You can:
- Adjust durations and easing
- Add new animations
- Modify hover effects and transitions

## Future Planned Improvements

- [ ] Google Maps integration for locations
- [ ] Image gallery with Splide.js
- [ ] Dark mode
- [ ] Advanced filters (age, orientation)
- [ ] Save comparisons
- [ ] PDF report generation
- [ ] Combined filters with AND/OR logic
- [ ] Map view with markers

## Contributions

Contributions are welcome. Please:
1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is under the MIT License. See `LICENSE` file for more details.

## Contact

For questions or support, please open an issue in the repository.

---

**PropertyAnalyzer** - Analyze properties like a professional 🏡📊
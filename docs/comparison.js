// Variables globales
let selectedProperties = [];
let comparisonCharts = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    loadSelectedProperties();
    setupP5Background();
});

function setupP5Background() {
    new p5((sketch) => {
        let particles = [];

        sketch.setup = function () {
            let canvas = sketch.createCanvas(sketch.windowWidth, sketch.windowHeight);
            canvas.parent('p5-background');

            // Crear partículas
            for (let i = 0; i < 30; i++) {
                particles.push({
                    x: sketch.random(sketch.width),
                    y: sketch.random(sketch.height),
                    vx: sketch.random(-0.5, 0.5),
                    vy: sketch.random(-0.5, 0.5),
                    size: sketch.random(3, 8)
                });
            }
        };

        sketch.draw = function () {
            sketch.clear();

            // Dibujar y actualizar partículas
            particles.forEach(p => {
                sketch.fill(37, 99, 235, 80);
                sketch.noStroke();
                sketch.circle(p.x, p.y, p.size);

                p.x += p.vx;
                p.y += p.vy;

                // Rebotar en los bordes
                if (p.x < 0 || p.x > sketch.width) p.vx *= -1;
                if (p.y < 0 || p.y > sketch.height) p.vy *= -1;
            });
        };

        sketch.windowResized = function () {
            sketch.resizeCanvas(sketch.windowWidth, sketch.windowHeight);
        };
    });
}

function loadSelectedProperties() {
    // Cargar desde localStorage
    const stored = localStorage.getItem('selectedProperties');
    if (stored) {
        selectedProperties = JSON.parse(stored);
    }

    if (selectedProperties.length === 0) {
        showNoPropertiesAlert();
    } else {
        hideNoPropertiesAlert();
        displayPropertyCards();
        displayComparisonTable();
        createComparisonCharts();
        analyzeDifferences();
        generateRecommendations();
        animateElements();
    }
}

function showNoPropertiesAlert() {
    document.getElementById('no-properties-alert').classList.remove('hidden');
    document.getElementById('property-cards').classList.add('hidden');
    document.getElementById('comparison-table-container').classList.add('hidden');
}

function hideNoPropertiesAlert() {
    document.getElementById('no-properties-alert').classList.add('hidden');
    document.getElementById('property-cards').classList.remove('hidden');
    document.getElementById('comparison-table-container').classList.remove('hidden');
}

function displayPropertyCards() {
    const container = document.getElementById('property-cards');
    container.innerHTML = '';

    selectedProperties.forEach((property, index) => {
        const card = createPropertyCard(property, index);
        container.appendChild(card);
    });
}

function createPropertyCard(property, index) {
    const card = document.createElement('div');
    card.className = 'comparison-card glass-effect rounded-xl p-6';

    const features = [];
    if (property.tiene_patio) features.push('Patio');
    if (property.tiene_quincho) features.push('Quincho');
    if (property.tiene_pileta) features.push('Pileta');
    if (property.tiene_cochera) features.push('Cochera');
    if (property.tiene_balcon) features.push('Balcón');
    if (property.tiene_terraza) features.push('Terraza');

    card.innerHTML = `
        <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-semibold text-gray-800">Propiedad ${index + 1}</h3>
            <div class="flex items-center space-x-2">
                <a href="${property.url}" target="_blank" rel="noopener noreferrer" 
                   class="text-blue-600 hover:text-blue-800 transition-colors" title="Ver publicación original">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                </a>
                <button onclick="removeProperty(${property.id})" class="text-red-500 hover:text-red-700" title="Eliminar de comparación">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>
        
        <div class="space-y-3">
            <div>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${property.tipo_inmueble === 'casa' ? 'bg-green-100 text-green-800' :
            property.tipo_inmueble === 'departamento' ? 'bg-blue-100 text-blue-800' :
                'bg-purple-100 text-purple-800'}">
                    ${property.tipo_inmueble}
                </span>
            </div>
            
            <div>
                <p class="text-sm font-medium text-gray-900">${property.direccion}</p>
                <p class="text-sm text-gray-500">${property.barrio}</p>
            </div>
            
            <div class="border-t pt-3">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm text-gray-600">Precio:</span>
                    <span class="text-lg font-bold text-blue-600 mono-font">${property.precio.toLocaleString('es-AR')} ${property.moneda || 'USD'}</span>
                </div>
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm text-gray-600">Superficie:</span>
                    <span class="text-sm font-medium mono-font">${property.metros_cuadrados_totales} m²</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600">Costo/m²:</span>
                    <span class="text-sm font-medium mono-font">${property.costo_metro_cuadrado.toLocaleString('es-AR')} ${property.moneda || 'USD'}</span>
                </div>
            </div>
            
            <div class="border-t pt-3">
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Dormitorios:</span>
                        <span class="font-medium">${property.cantidad_dormitorios}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Baños:</span>
                        <span class="font-medium">${property.cantidad_banos}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Ambientes:</span>
                        <span class="font-medium">${property.cantidad_ambientes}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Antigüedad:</span>
                        <span class="font-medium">${property.antiguedad}</span>
                    </div>
                </div>
            </div>
            
            ${features.length > 0 ? `
                <div class="border-t pt-3">
                    <p class="text-sm text-gray-600 mb-2">Características:</p>
                    <div class="flex flex-wrap gap-1">
                        ${features.map(feature =>
                    `<span class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">${feature}</span>`
                ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    return card;
}

function displayComparisonTable() {
    const tableBody = document.getElementById('comparison-table-body');
    const features = [
        { key: 'tipo_inmueble', label: 'Tipo de Inmueble' },
        { key: 'direccion', label: 'Dirección' },
        { key: 'barrio', label: 'Barrio' },
        { key: 'precio', label: 'Precio', format: 'currency' },
        { key: 'metros_cuadrados_cubiertos', label: 'M² Cubiertos', format: 'number' },
        { key: 'metros_cuadrados_totales', label: 'M² Totales', format: 'number' },
        { key: 'costo_metro_cuadrado', label: 'Costo/m²', format: 'currency' },
        { key: 'cantidad_dormitorios', label: 'Dormitorios', format: 'number' },
        { key: 'cantidad_banos', label: 'Baños', format: 'number' },
        { key: 'cantidad_ambientes', label: 'Ambientes', format: 'number' },
        { key: 'tiene_patio', label: 'Tiene Patio', format: 'boolean' },
        { key: 'tiene_quincho', label: 'Tiene Quincho', format: 'boolean' },
        { key: 'tiene_pileta', label: 'Tiene Pileta', format: 'boolean' },
        { key: 'tiene_cochera', label: 'Tiene Cochera', format: 'boolean' },
        { key: 'tiene_balcon', label: 'Tiene Balcón', format: 'boolean' },
        { key: 'tiene_terraza', label: 'Tiene Terraza', format: 'boolean' },
        { key: 'orientacion', label: 'Orientación' },
        { key: 'antiguedad', label: 'Antigüedad' },
        { key: 'status', label: 'Estado' }
    ];

    tableBody.innerHTML = '';

    features.forEach(feature => {
        const row = document.createElement('tr');
        row.className = 'feature-row';

        let html = `<td class="px-6 py-4 text-sm font-medium text-gray-900">${feature.label}</td>`;

        const values = selectedProperties.map(p => p[feature.key]);
        const hasDifferences = new Set(values).size > 1;

        selectedProperties.forEach(property => {
            let value = property[feature.key];
            let formattedValue = value;

            if (feature.format === 'currency' && typeof value === 'number') {
                const currency = property.moneda || 'USD';
                formattedValue = `${value.toLocaleString('es-AR')} ${currency}`;
            } else if (feature.format === 'number' && typeof value === 'number') {
                formattedValue = value.toString();
            } else if (feature.format === 'boolean') {
                formattedValue = value ? 'Sí' : 'No';
            } else if (value === null || value === undefined || value === '') {
                formattedValue = '-';
            }

            const cellClass = hasDifferences ? 'highlight-difference' : '';
            html += `<td class="px-6 py-4 text-sm text-gray-900 ${cellClass} mono-font">${formattedValue}</td>`;
        });

        row.innerHTML = html;
        tableBody.appendChild(row);
    });
}

function createComparisonCharts() {
    createPriceChart();
    createAreaChart();
    createFeaturesChart();
    createCostChart();
}

function createPriceChart() {
    const chart = echarts.init(document.getElementById('price-chart'));
    const currency = selectedProperties[0].moneda || 'USD';

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        xAxis: {
            type: 'category',
            data: selectedProperties.map((_, index) => `Propiedad ${index + 1}`)
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: `{value} ${currency}`
            }
        },
        series: [{
            data: selectedProperties.map(p => p.precio),
            type: 'bar',
            itemStyle: {
                color: '#2563eb'
            },
            label: {
                show: true,
                position: 'top',
                formatter: `{c} ${currency}`
            }
        }]
    };

    chart.setOption(option);
    comparisonCharts.price = chart;
}

function createAreaChart() {
    const chart = echarts.init(document.getElementById('area-chart'));

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['M² Cubiertos', 'M² Totales']
        },
        xAxis: {
            type: 'category',
            data: selectedProperties.map((_, index) => `Propiedad ${index + 1}`)
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: '{value} m²'
            }
        },
        series: [
            {
                name: 'M² Cubiertos',
                type: 'bar',
                data: selectedProperties.map(p => p.metros_cuadrados_cubiertos),
                itemStyle: { color: '#059669' }
            },
            {
                name: 'M² Totales',
                type: 'bar',
                data: selectedProperties.map(p => p.metros_cuadrados_totales),
                itemStyle: { color: '#64748b' }
            }
        ]
    };

    chart.setOption(option);
    comparisonCharts.area = chart;
}

function createFeaturesChart() {
    const chart = echarts.init(document.getElementById('features-chart'));

    const features = ['Patio', 'Quincho', 'Pileta', 'Cochera', 'Balcón', 'Terraza'];
    const featureKeys = ['tiene_patio', 'tiene_quincho', 'tiene_pileta', 'tiene_cochera', 'tiene_balcon', 'tiene_terraza'];

    const series = featureKeys.map((key, index) => ({
        name: features[index],
        type: 'bar',
        data: selectedProperties.map(p => p[key] ? 1 : 0),
        itemStyle: {
            color: ['#2563eb', '#059669', '#dc2626', '#7c3aed', '#f59e0b', '#06b6d4'][index]
        }
    }));

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: features
        },
        xAxis: {
            type: 'category',
            data: selectedProperties.map((_, index) => `Propiedad ${index + 1}`)
        },
        yAxis: {
            type: 'value',
            max: 1,
            axisLabel: {
                formatter: value => value === 1 ? 'Sí' : 'No'
            }
        },
        series: series
    };

    chart.setOption(option);
    comparisonCharts.features = chart;
}

function createCostChart() {
    const chart = echarts.init(document.getElementById('cost-chart'));
    const currency = selectedProperties[0].moneda || 'USD';

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        xAxis: {
            type: 'category',
            data: selectedProperties.map((_, index) => `Propiedad ${index + 1}`)
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: `{value} ${currency}/m²`
            }
        },
        series: [{
            data: selectedProperties.map(p => p.costo_metro_cuadrado),
            type: 'bar',
            itemStyle: {
                color: '#7c3aed'
            },
            label: {
                show: true,
                position: 'top',
                formatter: `{c} ${currency}/m²`
            }
        }]
    };

    chart.setOption(option);
    comparisonCharts.cost = chart;
}

function analyzeDifferences() {
    const container = document.getElementById('differences-content');
    let analysis = '';

    // Análisis de precios
    const prices = selectedProperties.map(p => p.precio);
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceDiff = maxPrice - minPrice;
    const currency = selectedProperties[0].moneda || 'USD';

    if (priceDiff > 0) {
        const maxIndex = prices.indexOf(maxPrice);
        const minIndex = prices.indexOf(minPrice);
        analysis += `<div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Diferencia de Precios</h4>
            <p class="text-gray-600">La Propiedad ${maxIndex + 1} es la más cara (${maxPrice.toLocaleString('es-AR')} ${currency}) y la Propiedad ${minIndex + 1} es la más barata (${minPrice.toLocaleString('es-AR')} ${currency}). La diferencia es de ${priceDiff.toLocaleString('es-AR')} ${currency}.</p>
        </div>`;
    }

    // Análisis de superficie
    const areas = selectedProperties.map(p => p.metros_cuadrados_totales);
    const maxArea = Math.max(...areas);
    const minArea = Math.min(...areas);
    const areaDiff = maxArea - minArea;

    if (areaDiff > 0) {
        const maxIndex = areas.indexOf(maxArea);
        const minIndex = areas.indexOf(minArea);
        analysis += `<div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Diferencia de Superficie</h4>
            <p class="text-gray-600">La Propiedad ${maxIndex + 1} es la más grande (${maxArea} m²) y la Propiedad ${minIndex + 1} es la más pequeña (${minArea} m²). La diferencia es de ${areaDiff} m².</p>
        </div>`;
    }

    // Análisis de características
    const features = ['tiene_patio', 'tiene_quincho', 'tiene_pileta', 'tiene_cochera', 'tiene_balcon', 'tiene_terraza'];
    const featureNames = ['Patio', 'Quincho', 'Pileta', 'Cochera', 'Balcón', 'Terraza'];

    features.forEach((feature, index) => {
        const values = selectedProperties.map(p => p[feature]);
        const hasVariation = new Set(values).size > 1;

        if (hasVariation) {
            const hasFeature = selectedProperties.map((p, i) => p[feature] ? `Propiedad ${i + 1}` : null).filter(Boolean);
            const noFeature = selectedProperties.map((p, i) => !p[feature] ? `Propiedad ${i + 1}` : null).filter(Boolean);

            analysis += `<div class="mb-4">
                <h4 class="font-semibold text-gray-800 mb-2">${featureNames[index]}</h4>
                <p class="text-gray-600">
                    ${hasFeature.length > 0 ? `La${hasFeature.length > 1 ? 's' : ''} ${hasFeature.join(', ')} ${hasFeature.length > 1 ? 'tienen' : 'tiene'} ${featureNames[index].toLowerCase()}.` : ''}
                    ${noFeature.length > 0 ? ` La${noFeature.length > 1 ? 's' : ''} ${noFeature.join(', ')} ${noFeature.length > 1 ? 'no tienen' : 'no tiene'}.` : ''}
                </p>
            </div>`;
        }
    });

    container.innerHTML = analysis || '<p class="text-gray-600">No se encontraron diferencias significativas entre las propiedades seleccionadas.</p>';
}

function generateRecommendations() {
    const container = document.getElementById('recommendations-content');
    let recommendations = '';

    // Recomendación basada en precio por m²
    // Recomendación basada en precio por m²
    // Usamos el costo_metro_cuadrado que ya viene de la base de datos
    const propertiesWithCost = selectedProperties.map(p => {
        let cost = p.costo_metro_cuadrado;
        if (typeof cost === 'string') {
            cost = parseFloat(cost.replace('.', '').replace(',', '.'));
        }
        return {
            ...p,
            costPerM2: (typeof cost === 'number' && !isNaN(cost)) ? cost : Infinity
        };
    });

    propertiesWithCost.sort((a, b) => a.costPerM2 - b.costPerM2);
    const bestValue = propertiesWithCost[0];
    const bestValueIndex = selectedProperties.findIndex(p => p.id === bestValue.id) + 1;
    const currency = bestValue.moneda || 'USD';

    recommendations += `<div class="mb-4">
        <h4 class="font-semibold text-gray-800 mb-2">Mejor Relación Precio/Superficie</h4>
        <p class="text-gray-600">La Propiedad ${bestValueIndex} ofrece la mejor relación precio por metro cuadrado a ${bestValue.costPerM2.toLocaleString('es-AR')} ${currency}/m².</p>
    </div>`;

    // Recomendación basada en características
    const featureCounts = selectedProperties.map((p, index) => {
        const features = [p.tiene_patio, p.tiene_quincho, p.tiene_pileta, p.tiene_cochera, p.tiene_balcon, p.tiene_terraza];
        const count = features.filter(Boolean).length;
        return { index: index + 1, count };
    });

    const mostFeatures = featureCounts.reduce((max, current) => current.count > max.count ? current : max);

    if (mostFeatures.count > 0) {
        recommendations += `<div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Más Características</h4>
            <p class="text-gray-600">La Propiedad ${mostFeatures.index} tiene más características adicionales (${mostFeatures.count} en total).</p>
        </div>`;
    }

    // Recomendación basada en antigüedad
    const newProperties = selectedProperties.filter(p => p.antiguedad === 'nueva');
    if (newProperties.length > 0) {
        recommendations += `<div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Propiedades Nuevas</h4>
            <p class="text-gray-600">${newProperties.length === 1 ? 'Una propiedad' : `${newProperties.length} propiedades`} ${newProperties.length === 1 ? 'es' : 'son'} nueva${newProperties.length === 1 ? '' : 's'}, lo que puede significar menos gastos de mantenimiento a corto plazo.</p>
        </div>`;
    }

    container.innerHTML = recommendations || '<p class="text-gray-600">No hay recomendaciones específicas basadas en las propiedades seleccionadas.</p>';
}

function removeProperty(propertyId) {
    selectedProperties = selectedProperties.filter(p => p.id !== propertyId);

    if (selectedProperties.length < 2) {
        // Si queda menos de 2 propiedades, redirigir a la página principal
        localStorage.removeItem('selectedProperties');
        window.location.href = 'index.html';
    } else {
        // Actualizar localStorage y recargar la comparación
        localStorage.setItem('selectedProperties', JSON.stringify(selectedProperties));
        location.reload();
    }
}

function viewDetailedComparison() {
    // Esta función podría abrir un modal más detallado o generar un PDF
    alert('Función de comparación detallada - Aquí se podría generar un reporte PDF o mostrar más detalles.');
}

function exportComparison() {
    // Crear CSV con las propiedades comparadas
    if (selectedProperties.length === 0) {
        alert('No hay propiedades seleccionadas para exportar.');
        return;
    }

    const headers = Object.keys(selectedProperties[0]).join(',');
    const csvContent = [
        headers,
        ...selectedProperties.map(row => Object.values(row).join(','))
    ].join('\n');

    // Descargar archivo
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'comparacion_propiedades.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

function animateElements() {
    // Animar tarjetas de propiedades
    anime({
        targets: '.comparison-card',
        opacity: [0, 1],
        translateY: [30, 0],
        delay: anime.stagger(200),
        duration: 800,
        easing: 'easeOutExpo'
    });

    // Animar filas de la tabla
    anime({
        targets: '.feature-row',
        opacity: [0, 1],
        translateX: [-20, 0],
        delay: anime.stagger(50, { start: 500 }),
        duration: 600,
        easing: 'easeOutExpo'
    });
}

// Redimensionar gráficos al cambiar el tamaño de la ventana
window.addEventListener('resize', function () {
    Object.values(comparisonCharts).forEach(chart => {
        chart.resize();
    });
});

// Limpiar datos al salir de la página
window.addEventListener('beforeunload', function () {
    localStorage.removeItem('selectedProperties');
});
// Variables globales
let propertiesData = [];
// Mapeo de tipos de datos para conversión
const typeMapping = {
    id: (v) => parseInt(v),
    metros_cuadrados_cubiertos: (v) => parseFloat(v) || 0,
    metros_cuadrados_totales: (v) => parseFloat(v) || 0,
    precio: (v) => parseFloat(v) || 0,
    cantidad_dormitorios: (v) => parseInt(v) || 0,
    cantidad_banos: (v) => parseInt(v) || 0,
    cantidad_ambientes: (v) => parseInt(v) || 0,
    tiene_patio: (v) => parseInt(v) || 0,
    tiene_quincho: (v) => parseInt(v) || 0,
    tiene_pileta: (v) => parseInt(v) || 0,
    tiene_cochera: (v) => parseInt(v) || 0,
    tiene_balcon: (v) => parseInt(v) || 0,
    tiene_terraza: (v) => parseInt(v) || 0,
    costo_metro_cuadrado: (v) => parseFloat(v) || 0,
    status: (v) => v || 'NO_STATUS'
};

async function fetchProperties() {
    try {
        const response = await fetch('properties_export.csv?t=' + new Date().getTime());
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        propertiesData = parseCSV(text);

        // Inicializar la app una vez cargados los datos
        initializeApp();
    } catch (error) {
        console.error('Error loading properties:', error);
        document.getElementById('properties-table').innerHTML = `
            <tr>
                <td colspan="9" class="px-6 py-4 text-center text-red-600">
                    Error cargando los datos. Si estás ejecutando localmente, asegúrate de usar un servidor web local (ej: python -m http.server) en lugar de abrir el archivo directamente.
                </td>
            </tr>
        `;
    }
}

function parseCSV(csvText) {
    const lines = csvText.split('\n').filter(line => line.trim() !== '');
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map(h => h.trim());

    return lines.slice(1).map(line => {
        const obj = {};
        let currentLine = '';
        let inQuotes = false;
        let values = [];

        // Parsear respetando comillas
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(currentLine.trim());
                currentLine = '';
            } else {
                currentLine += char;
            }
        }
        values.push(currentLine.trim());

        // Asegurarse de quitar comillas de los valores
        values = values.map(v => v.replace(/^"|"$/g, ''));

        headers.forEach((header, index) => {
            const value = values[index];
            if (typeMapping[header]) {
                obj[header] = typeMapping[header](value);
            } else {
                obj[header] = value;
            }
        });

        // Asegurar campos requeridos para la UI
        obj.tipo_inmueble = (obj.tipo_inmueble || 'otro').toLowerCase();
        obj.tipo_operacion = (obj.tipo_operacion || 'venta').toLowerCase();

        return obj;
    });
}

// Variables globales
let filteredData = [];
let selectedProperties = new Set();
let currentPage = 1;
const itemsPerPage = 10;
let currentSort = { field: null, direction: 'asc' };

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    fetchProperties();
    setupEventListeners();
    setupP5Background();
});

function initializeApp() {
    filteredData = [...propertiesData];
    loadProperties();
    updateStatistics();
    animateTitle();
}

function setupEventListeners() {
    // Búsqueda en tiempo real
    document.getElementById('search-input').addEventListener('input', debounce(applyFilters, 300));

    // Filtros
    document.getElementById('operation-filter').addEventListener('change', applyFilters);
    document.getElementById('property-filter').addEventListener('change', applyFilters);
    document.getElementById('price-min').addEventListener('input', debounce(applyFilters, 500));
    document.getElementById('price-max').addEventListener('input', debounce(applyFilters, 500));

    // Filtro de status
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }

    // Filtros de dormitorios
    document.querySelectorAll('[data-dormitorios]').forEach(btn => {
        btn.addEventListener('click', function () {
            this.classList.toggle('bg-blue-600');
            this.classList.toggle('text-white');
            this.classList.toggle('bg-gray-200');
            applyFilters();
        });
    });
}

function setupP5Background() {
    new p5((sketch) => {
        let particles = [];

        sketch.setup = function () {
            let canvas = sketch.createCanvas(sketch.windowWidth, sketch.windowHeight);
            canvas.parent('p5-background');

            // Crear partículas
            for (let i = 0; i < 50; i++) {
                particles.push({
                    x: sketch.random(sketch.width),
                    y: sketch.random(sketch.height),
                    vx: sketch.random(-1, 1),
                    vy: sketch.random(-1, 1),
                    size: sketch.random(2, 6)
                });
            }
        };

        sketch.draw = function () {
            sketch.clear();

            // Dibujar y actualizar partículas
            particles.forEach(p => {
                sketch.fill(37, 99, 235, 100);
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

function animateTitle() {
    anime({
        targets: '#main-title',
        opacity: [0, 1],
        translateY: [30, 0],
        duration: 1000,
        easing: 'easeOutExpo'
    });
}

function loadProperties() {
    const tableBody = document.getElementById('properties-table');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredData.slice(startIndex, endIndex);

    tableBody.innerHTML = '';

    pageData.forEach((property, index) => {
        const row = createTableRow(property, startIndex + index);
        tableBody.appendChild(row);
    });

    updatePagination();
    updateShowingCount();

    // Animar filas
    anime({
        targets: '.table-row',
        opacity: [0, 1],
        translateX: [-20, 0],
        delay: anime.stagger(100),
        duration: 500,
        easing: 'easeOutExpo'
    });
}

function createTableRow(property, index) {
    const row = document.createElement('tr');
    row.className = 'table-row';
    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
            <input type="checkbox" class="property-checkbox" data-id="${property.id}" 
                   onchange="togglePropertySelection(${property.id})" 
                   ${selectedProperties.has(property.id) ? 'checked' : ''}>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <a href="${property.url}" target="_blank" rel="noopener noreferrer" 
               class="text-blue-600 hover:text-blue-800 transition-colors" title="Ver publicación original">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
            </a>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${getStatusStyle(property.status)}">
                ${getStatusLabel(property.status)}
            </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${property.tipo_inmueble === 'casa' ? 'bg-green-100 text-green-800' :
            property.tipo_inmueble === 'departamento' ? 'bg-blue-100 text-blue-800' :
                'bg-purple-100 text-purple-800'}">
                ${property.tipo_inmueble}
            </span>
        </td>
        <td class="px-6 py-4">
            <div class="text-sm font-medium text-gray-900">${property.direccion}</div>
            <div class="text-sm text-gray-500">${property.barrio}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            ${property.barrio}
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm font-medium text-gray-900 mono-font">
                ${property.precio.toLocaleString('es-AR')} ${property.moneda || 'USD'}
            </div>
            <div class="text-xs text-gray-500 mono-font">
                ${property.costo_metro_cuadrado.toLocaleString('es-AR')} ${property.moneda || 'USD'}/m²
            </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 mono-font">
            ${property.metros_cuadrados_totales} m²
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            ${property.cantidad_dormitorios} dorm
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            ${property.cantidad_banos} baños
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
            <button onclick="viewPropertyDetails(${property.id})" 
                    class="text-blue-600 hover:text-blue-900 transition-colors">
                Ver Detalles
            </button>
        </td>
    `;

    return row;
}

function togglePropertySelection(propertyId) {
    if (selectedProperties.has(propertyId)) {
        // Deseleccionar
        selectedProperties.delete(propertyId);
    } else {
        // Intentar seleccionar
        if (selectedProperties.size >= 3) {
            alert('Solo se pueden seleccionar hasta 3 propiedades para comparar.');
            // Revertir el check visual
            const checkbox = document.querySelector(`.property-checkbox[data-id="${propertyId}"]`);
            if (checkbox) checkbox.checked = false;
            return;
        }
        selectedProperties.add(propertyId);
    }

    updateSelectionUI();
    updateComparisonButton();
}

function toggleSelectAll() {
    const masterCheckbox = document.getElementById('master-checkbox');
    const checkboxes = document.querySelectorAll('.property-checkbox[data-id]');

    if (masterCheckbox.checked) {
        // Seleccionar máximo 3
        let count = 0;
        selectedProperties.clear(); // Limpiamos para asegurar start fresco

        checkboxes.forEach(checkbox => {
            if (count < 3) {
                const propertyId = parseInt(checkbox.dataset.id);
                selectedProperties.add(propertyId);
                checkbox.checked = true;
                count++;
            } else {
                checkbox.checked = false;
            }
        });

        if (checkboxes.length > 3) {
            alert('Se han seleccionado las primeras 3 propiedades (límite máximo permitido).');
        }
    } else {
        // Deseleccionar todo
        checkboxes.forEach(checkbox => {
            const propertyId = parseInt(checkbox.dataset.id);
            selectedProperties.delete(propertyId);
            checkbox.checked = false;
        });
        selectedProperties.clear();
    }

    updateSelectionUI();
    updateComparisonButton();
}

function updateSelectionUI() {
    const selectedCount = selectedProperties.size;
    document.getElementById('selected-count').textContent = selectedCount;

    // Actualizar estado del checkbox maestro
    const masterCheckbox = document.getElementById('master-checkbox');
    const totalVisible = filteredData.length;
    const selectedVisible = filteredData.filter(p => selectedProperties.has(p.id)).length;

    if (selectedVisible === 0) {
        masterCheckbox.checked = false;
        masterCheckbox.indeterminate = false;
    } else if (selectedVisible === totalVisible) {
        masterCheckbox.checked = true;
        masterCheckbox.indeterminate = false;
    } else {
        masterCheckbox.checked = false;
        masterCheckbox.indeterminate = true;
    }
}

function updateComparisonButton() {
    const compareBtn = document.getElementById('compare-btn');
    const compareCount = document.getElementById('compare-count');
    const selectedCount = selectedProperties.size;

    compareCount.textContent = selectedCount;
    compareBtn.disabled = selectedCount < 2;

    if (selectedCount >= 2) {
        compareBtn.classList.add('pulse-animation');
    } else {
        compareBtn.classList.remove('pulse-animation');
    }
}

function updateStatistics() {
    const totalProperties = propertiesData.length;
    const avgPrice = propertiesData.reduce((sum, p) => sum + p.precio, 0) / totalProperties;
    const totalVenta = propertiesData.filter(p => p.tipo_operacion === 'venta').length;

    document.getElementById('total-properties').textContent = totalProperties;
    document.getElementById('avg-price').textContent = `$${Math.round(avgPrice).toLocaleString('es-AR')}`;
    document.getElementById('total-venta').textContent = totalVenta;

    // Animar números
    animateNumbers();
}

function animateNumbers() {
    anime({
        targets: '#total-properties',
        innerHTML: [0, parseInt(document.getElementById('total-properties').textContent)],
        duration: 1000,
        round: 1,
        easing: 'easeOutExpo'
    });
}

function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const operationFilter = document.getElementById('operation-filter').value;
    const propertyFilter = document.getElementById('property-filter').value;
    const priceMin = parseFloat(document.getElementById('price-min').value) || 0;
    const priceMax = parseFloat(document.getElementById('price-max').value) || Infinity;
    const statusFilter = document.getElementById('status-filter') ? document.getElementById('status-filter').value : '';

    // Obtener filtros de dormitorios seleccionados
    const selectedDormitorios = Array.from(document.querySelectorAll('[data-dormitorios].bg-blue-600'))
        .map(btn => btn.dataset.dormitorios);

    filteredData = propertiesData.filter(property => {
        // Búsqueda
        const matchesSearch = !searchTerm ||
            property.direccion.toLowerCase().includes(searchTerm) ||
            property.barrio.toLowerCase().includes(searchTerm) ||
            property.descripcion_breve.toLowerCase().includes(searchTerm);

        // Tipo de operación
        const matchesOperation = !operationFilter || property.tipo_operacion === operationFilter;

        // Tipo de inmueble
        const matchesProperty = !propertyFilter || property.tipo_inmueble === propertyFilter;

        // Rango de precio
        const matchesPrice = property.precio >= priceMin && property.precio <= priceMax;

        // Status
        let matchesStatus = true;
        if (statusFilter) {
            if (statusFilter === 'NO_STATUS') {
                matchesStatus = !property.status || property.status === 'NO_STATUS' || property.status === '';
            } else {
                matchesStatus = property.status === statusFilter;
            }
        }

        // Dormitorios
        const matchesDormitorios = selectedDormitorios.length === 0 ||
            selectedDormitorios.some(d => {
                if (d === '4+') return property.cantidad_dormitorios >= 4;
                return property.cantidad_dormitorios === parseInt(d);
            });

        return matchesSearch && matchesOperation && matchesProperty && matchesPrice && matchesDormitorios && matchesStatus;
    });

    currentPage = 1;
    loadProperties();
    updateActiveFilters();
}

function updateActiveFilters() {
    const activeFiltersDiv = document.getElementById('active-filters');
    const filterChipsDiv = document.getElementById('filter-chips');

    const filters = [];

    if (document.getElementById('search-input').value) {
        filters.push({ type: 'search', value: document.getElementById('search-input').value });
    }
    if (document.getElementById('operation-filter').value) {
        filters.push({ type: 'operation', value: document.getElementById('operation-filter').value });
    }
    if (document.getElementById('property-filter').value) {
        filters.push({ type: 'property', value: document.getElementById('property-filter').value });
    }
    if (document.getElementById('price-min').value || document.getElementById('price-max').value) {
        filters.push({ type: 'price', value: `${document.getElementById('price-min').value || 0} - ${document.getElementById('price-max').value || '∞'}` });
    }
    if (document.getElementById('status-filter') && document.getElementById('status-filter').value) {
        filters.push({ type: 'status', value: document.getElementById('status-filter').value });
    }

    if (filters.length > 0) {
        activeFiltersDiv.classList.remove('hidden');
        filterChipsDiv.innerHTML = filters.map(filter =>
            `<span class="filter-chip inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                ${filter.type}: ${filter.value}
                <button onclick="clearFilter('${filter.type}')" class="ml-1 text-blue-600 hover:text-blue-800">×</button>
            </span>`
        ).join('');
    } else {
        activeFiltersDiv.classList.add('hidden');
    }
}

function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('operation-filter').value = '';
    document.getElementById('property-filter').value = '';
    document.getElementById('price-min').value = '';
    document.getElementById('price-max').value = '';
    if (document.getElementById('status-filter')) {
        document.getElementById('status-filter').value = '';
    }

    // Limpiar filtros de dormitorios
    document.querySelectorAll('[data-dormitorios].bg-blue-600').forEach(btn => {
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-gray-200');
    });

    applyFilters();
}

function sortTable(field) {
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'asc';
    }

    filteredData.sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];

        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }

        if (currentSort.direction === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    loadProperties();
}

function updatePagination() {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageNumbers = document.getElementById('page-numbers');

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    // Actualizar números de página
    pageNumbers.innerHTML = '';
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = `px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors ${i === currentPage ? 'bg-blue-600 text-white' : ''}`;
        pageBtn.onclick = () => goToPage(i);
        pageNumbers.appendChild(pageBtn);
    }

    // Actualizar contadores
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredData.length);

    document.getElementById('page-start').textContent = startIndex;
    document.getElementById('page-end').textContent = endIndex;
    document.getElementById('total-results').textContent = filteredData.length;
}

function changePage(direction) {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    const newPage = currentPage + direction;

    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadProperties();
    }
}

function goToPage(page) {
    currentPage = page;
    loadProperties();
}

function updateShowingCount() {
    document.getElementById('showing-count').textContent =
        `Mostrando ${filteredData.length} de ${propertiesData.length} propiedades`;
}

function openComparison() {
    if (selectedProperties.size >= 2) {
        // Guardar selección en localStorage para la página de comparación
        const selectedData = Array.from(selectedProperties).map(id =>
            propertiesData.find(p => p.id === id)
        );
        localStorage.setItem('selectedProperties', JSON.stringify(selectedData));

        // Redirigir a la página de comparación
        window.location.href = 'comparison.html';
    }
}

function viewPropertyDetails(propertyId) {
    const property = propertiesData.find(p => p.id === propertyId);
    if (property) {
        // Crear modal o redirigir a página de detalles
        alert(`Detalles de la propiedad:\n\n` +
            `Dirección: ${property.direccion}\n` +
            `Barrio: ${property.barrio}\n` +
            `Precio: $${property.precio.toLocaleString('es-AR')} USD\n` +
            `Superficie: ${property.metros_cuadrados_totales} m²\n` +
            `Dormitorios: ${property.cantidad_dormitorios}\n` +
            `Baños: ${property.cantidad_banos}\n\n` +
            `Descripción: ${property.descripcion_breve}`);
    }
}

function exportData() {
    // Crear CSV con los datos filtrados
    const headers = Object.keys(propertiesData[0]).join(',');
    const csvContent = [
        headers,
        ...filteredData.map(row => Object.values(row).join(','))
    ].join('\n');

    // Descargar archivo
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'propiedades_filtradas.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Función debounce para optimizar búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Funciones para el panel de comparación (si se usa en la misma página)
function closeComparison() {
    document.getElementById('comparison-panel').classList.remove('active');
}

function clearSelection() {
    selectedProperties.clear();
    updateSelectionUI();
    updateComparisonButton();
    loadProperties();
}

// Helpers para el estado
function getStatusStyle(status) {
    switch (status) {
        case 'YES': return 'bg-green-100 text-green-800';
        case 'MAYBE': return 'bg-yellow-100 text-yellow-800';
        case 'NO': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function getStatusLabel(status) {
    if (!status || status === 'NO_STATUS') return '-';
    return status;
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
// Monglo Relationship Graph - UML/ER Diagram Style

class MongloRelationshipGraph {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data;
        this.width = this.container.offsetWidth || 1200;
        this.height = 600;

        // Dark mode detection
        this.init();
    }

    init() {
        // Detect dark mode with multiple checks
        this.updateDarkMode();

        // Create SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', this.width);
        this.svg.setAttribute('height', this.height);
        this.updateSVGBackground();

        this.container.appendChild(this.svg);

        this.render();
    }

    updateDarkMode() {
        // Check body class first
        this.isDarkMode = document.body.classList.contains('dark-mode');

        // Fallback to localStorage if body class not set yet
        if (!this.isDarkMode) {
            const savedMode = localStorage.getItem('monglo-dark-mode');
            this.isDarkMode = savedMode === 'dark';
        }
    }

    updateSVGBackground() {
        this.svg.style.background = this.isDarkMode ? '#1a1a1a' : '#f9fafb';
        this.svg.style.borderRadius = 'var(--radius-lg)';
        this.svg.style.boxShadow = 'var(--shadow-sm)';
    }

    render() {
        const collections = this.data.collections;
        const relationships = this.data.relationships;

        // Calculate layout
        const boxWidth = 220;
        const boxHeight = 150;
        const cols = Math.min(3, collections.length);
        const rows = Math.ceil(collections.length / cols);

        const horizontalSpacing = (this.width - (cols * boxWidth)) / (cols + 1);
        const verticalSpacing = (this.height - (rows * boxHeight)) / (rows + 1);

        // Position collections
        const positions = new Map();
        collections.forEach((collection, index) => {
            const col = index % cols;
            const row = Math.floor(index / cols);

            const x = horizontalSpacing + col * (boxWidth + horizontalSpacing);
            const y = verticalSpacing + row * (boxHeight + verticalSpacing);

            positions.set(collection.name, { x, y, width: boxWidth, height: boxHeight });
        });

        // Add arrowhead marker
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 6 3, 0 6');
        polygon.setAttribute('fill', this.isDarkMode ? '#10b981' : '#10b981');
        marker.appendChild(polygon);
        defs.appendChild(marker);
        this.svg.appendChild(defs);

        // Draw relationships (lines) first so they appear behind boxes
        relationships.forEach(rel => {
            const source = positions.get(rel.source_collection);
            const target = positions.get(rel.target_collection);

            if (source && target) {
                this.drawRelationship(source, target, rel);
            }
        });

        // Draw collection boxes
        collections.forEach(collection => {
            const pos = positions.get(collection.name);
            if (pos) {
                this.drawCollectionBox(collection, pos);
            }
        });
    }

    drawRelationship(source, target, rel) {
        // Calculate connection points (center of boxes)
        const x1 = source.x + source.width / 2;
        const y1 = source.y + source.height / 2;
        const x2 = target.x + target.width / 2;
        const y2 = target.y + target.height / 2;

        // Calculate edge intersection points
        const sourceEdge = this.getBoxEdgePoint(source, x2, y2);
        const targetEdge = this.getBoxEdgePoint(target, x1, y1);

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', sourceEdge.x);
        line.setAttribute('y1', sourceEdge.y);
        line.setAttribute('x2', targetEdge.x);
        line.setAttribute('y2', targetEdge.y);


        // Color based on relationship type
        let color;
        if (rel.type === 'one_to_one') {
            color = this.isDarkMode ? '#10b981' : '#059669';  // Green
        } else if (rel.type === 'one_to_many') {
            color = this.isDarkMode ? '#60a5fa' : '#3b82f6';  // Blue
        } else if (rel.type === 'many_to_many') {
            color = this.isDarkMode ? '#fbbf24' : '#f59e0b';  // Orange
        } else if (rel.type === 'embedded') {
            color = this.isDarkMode ? '#a78bfa' : '#8b5cf6';  // Purple
        } else {
            color = this.isDarkMode ? '#9ca3af' : '#6b7280';  // Gray default
        }

        line.setAttribute('stroke', color);
        line.setAttribute('stroke-width', '2');
        line.setAttribute('marker-end', 'url(#arrowhead)');

        // Tooltip
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${rel.source_field} → ${rel.target_collection} (${rel.type})`;
        line.appendChild(title);

        this.svg.appendChild(line);
    }

    getBoxEdgePoint(box, targetX, targetY) {
        const centerX = box.x + box.width / 2;
        const centerY = box.y + box.height / 2;

        const dx = targetX - centerX;
        const dy = targetY - centerY;

        // Calculate intersection with box edges
        let x, y;

        if (Math.abs(dx) > Math.abs(dy)) {
            // Intersect left or right edge
            x = dx > 0 ? box.x + box.width : box.x;
            y = centerY + (dy / dx) * (x - centerX);
        } else {
            // Intersect top or bottom edge
            y = dy > 0 ? box.y + box.height : box.y;
            x = centerX + (dx / dy) * (y - centerY);
        }

        return { x, y };
    }

    drawCollectionBox(collection, pos) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.style.cursor = 'pointer';

        // Main box
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', pos.x);
        rect.setAttribute('y', pos.y);
        rect.setAttribute('width', pos.width);
        rect.setAttribute('height', pos.height);
        rect.setAttribute('fill', this.isDarkMode ? '#2d2d2d' : '#ffffff');
        rect.setAttribute('stroke', this.isDarkMode ? '#444' : '#e5e7eb');
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('rx', '8');

        // Header section
        const header = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        header.setAttribute('x', pos.x);
        header.setAttribute('y', pos.y);
        header.setAttribute('width', pos.width);
        header.setAttribute('height', '35');
        header.setAttribute('fill', this.isDarkMode ? '#10b981' : '#10b981');
        header.setAttribute('rx', '8');

        // Header text (collection name)
        const headerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        headerText.setAttribute('x', pos.x + pos.width / 2);
        headerText.setAttribute('y', pos.y + 22);
        headerText.setAttribute('text-anchor', 'middle');
        headerText.setAttribute('fill', '#ffffff');
        headerText.setAttribute('font-weight', '600');
        headerText.setAttribute('font-size', '14');
        headerText.textContent = collection.display_name || collection.name;

        // Field count text
        const fieldCountText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        fieldCountText.setAttribute('x', pos.x + pos.width / 2);
        fieldCountText.setAttribute('y', pos.y + 55);
        fieldCountText.setAttribute('text-anchor', 'middle');
        fieldCountText.setAttribute('fill', this.isDarkMode ? '#9ca3af' : '#6b7280');
        fieldCountText.setAttribute('font-size', '12');
        fieldCountText.textContent = `Documents: ${collection.count || 0}`;

        // Relationship count
        const relCountText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        relCountText.setAttribute('x', pos.x + pos.width / 2);
        relCountText.setAttribute('y', pos.y + 75);
        relCountText.setAttribute('text-anchor', 'middle');
        relCountText.setAttribute('fill', this.isDarkMode ? '#9ca3af' : '#6b7280');
        relCountText.setAttribute('font-size', '12');
        relCountText.textContent = `Relationships: ${collection.relationships || 0}`;

        // Icon
        const icon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        icon.setAttribute('x', pos.x + pos.width / 2);
        icon.setAttribute('y', pos.y + 110);
        icon.setAttribute('text-anchor', 'middle');
        icon.setAttribute('font-size', '32');
        icon.textContent = '📊';

        // Hover effect
        group.addEventListener('mouseenter', () => {
            rect.setAttribute('stroke', this.isDarkMode ? '#10b981' : '#10b981');
            rect.setAttribute('stroke-width', '3');
        });
        group.addEventListener('mouseleave', () => {
            rect.setAttribute('stroke', this.isDarkMode ? '#444' : '#e5e7eb');
            rect.setAttribute('stroke-width', '2');
        });

        // Click to navigate
        group.addEventListener('click', () => {
            window.location.href = `${window.MONGLO_PREFIX}/${collection.name}`;
        });

        group.appendChild(rect);
        group.appendChild(header);
        group.appendChild(headerText);
        group.appendChild(fieldCountText);
        group.appendChild(relCountText);
        group.appendChild(icon);
        this.svg.appendChild(group);
    }
}

// Export
window.MongloRelationshipGraph = MongloRelationshipGraph;

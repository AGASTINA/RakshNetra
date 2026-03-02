// Professional 2D Architecture Map Editor - Grid-Based with Wall Drawing

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class ArchitectureMapEditor {
    constructor(canvasId, containerEl) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas not found:', canvasId);
            return;
        }
        
        this.container = containerEl || this.canvas.parentElement;
        this.ctx = this.canvas.getContext('2d');
        
        // Initialize canvas size
        this.resizeCanvas();
        
        // Data structures
        this.layoutImage = null;
        this.walls = [];
        this.zones = []; // Rectangle zones for rooms
        this.objects = [];
        this.selectedTool = 'select';
        this.selectedObject = null;
        
        // Drawing state
        this.isDragging = false;
        this.isDrawingWall = false;
        this.isDrawingZone = false;
        this.wallStart = null;
        this.zoneStart = null;
        this.currentWall = null;
        this.currentZone = null;
        this.dragOffset = { x: 0, y: 0 };
        
        // Tracking mode
        this.trackingEnabled = false;
        this.terroristLocation = null;
        
        // Canvas view
        this.gridSize = 20;
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.panStart = { x: 0, y: 0 };
        
        // History
        this.history = [];
        this.historyIndex = -1;
        
        // Colors
        this.colors = {
            background: '#0f1419',
            grid: '#1a2332',
            gridMajor: '#2a3f5f',
            wall: '#4a5568',
            wallActive: '#667eea',
            camera: '#3b82f6',
            door: '#f59e0b',
            soldier: '#10b981',
            zone: '#ef4444',
            selected: '#fbbf24',
            text: '#e5e7eb'
        };
        
        this.init();
    }
    
    init() {
        console.log('ArchitectureMapEditor initialized - v2.0');
        this.setupEventListeners();
        this.loadBackgroundImage(); // Load background image from API
        this.render();
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    saveMapAs(filename) {
        // Save current map drawing with a custom filename
        const mapData = this.exportMap();
        
        console.log('Saving map as:', filename);
        
        // Save to localStorage temporarily
        localStorage.setItem(`map_${filename}`, JSON.stringify(mapData));
        
        alert(`Map saved as "${filename}"`);
        return true;
    }
    
    loadMapAs(filename) {
        // Load a previously saved map drawing
        const savedData = localStorage.getItem(`map_${filename}`);
        
        if (!savedData) {
            console.error('Map not found:', filename);
            alert('Map file not found');
            return false;
        }
        
        try {
            const mapData = JSON.parse(savedData);
            this.importMap(mapData);
            console.log('Map loaded:', filename);
            return true;
        } catch (error) {
            console.error('Error loading map:', error);
            alert('Error loading map file');
            return false;
        }
    }
    
    getListSavedMaps() {
        // Get list of all saved maps
        const maps = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('map_')) {
                const name = key.replace('map_', '');
                maps.push(name);
            }
        }
        return maps;
    }
    
    enableTracking(enable = true) {
        this.trackingEnabled = enable;
        console.log('Tracking mode:', enable ? 'ENABLED' : 'DISABLED');
        this.render();
    }
    
    updateTerroristLocation(x, y) {
        if (!this.trackingEnabled) return;
        
        console.log('Terrorist location updated:', x, y);
        this.terroristLocation = { x, y };
        
        // Move objects relative to terrorist location if tracking is enabled
        // For now just update the location
        this.render();
    }
    
    drawTerroristLocation() {
        if (!this.terroristLocation) return;
        
        // Draw terrorist marker
        const x = this.terroristLocation.x;
        const y = this.terroristLocation.y;
        
        this.ctx.fillStyle = '#ff1744';
        this.ctx.beginPath();
        this.ctx.arc(x, y, 12, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw indicator circle
        this.ctx.strokeStyle = '#ff1744';
        this.ctx.lineWidth = 2 / this.zoom;
        this.ctx.beginPath();
        this.ctx.arc(x, y, 20, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Draw label
        this.ctx.fillStyle = '#ff1744';
        this.ctx.font = `12px Arial`;
        this.ctx.fillText('TERRORIST', x + 25, y);
    }
    
    resizeCanvas() {
        const rect = this.container.getBoundingClientRect();
        const width = Math.max(800, rect.width);
        const height = Math.max(600, rect.height - 60); // Account for toolbar
        this.canvas.width = width;
        this.canvas.height = height;
        this.render();
    }
    
    setupEventListeners() {
        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }
    
    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.panX) / this.zoom;
        const y = (e.clientY - rect.top - this.panY) / this.zoom;
        return { x, y };
    }
    
    snapToGrid(x, y) {
        return {
            x: Math.round(x / this.gridSize) * this.gridSize,
            y: Math.round(y / this.gridSize) * this.gridSize
        };
    }
    
    handleMouseDown(e) {
        const pos = this.getMousePos(e);
        
        // Middle mouse button or space+click for panning
        if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
            this.isPanning = true;
            this.panStart = { x: e.clientX - this.panX, y: e.clientY - this.panY };
            this.canvas.style.cursor = 'grabbing';
            return;
        }
        
        if (this.selectedTool === 'wall') {
            const snapped = this.snapToGrid(pos.x, pos.y);
            this.isDrawingWall = true;
            this.wallStart = snapped;
            this.currentWall = { x1: snapped.x, y1: snapped.y, x2: snapped.x, y2: snapped.y };
        } else if (this.selectedTool === 'zone') {
            const snapped = this.snapToGrid(pos.x, pos.y);
            this.isDrawingZone = true;
            this.zoneStart = snapped;
            this.currentZone = { x: snapped.x, y: snapped.y, width: 0, height: 0 };
        } else if (this.selectedTool === 'select') {
            // Check if clicking on existing object
            const clickedObj = this.findObjectAt(pos.x, pos.y);
            const clickedWall = this.findWallAt(pos.x, pos.y);
            const clickedZone = this.findZoneAt(pos.x, pos.y);
            
            if (clickedObj) {
                this.selectedObject = clickedObj;
                this.isDragging = true;
                this.dragOffset = {
                    x: pos.x - clickedObj.x,
                    y: pos.y - clickedObj.y
                };
                this.canvas.style.cursor = 'move';
            } else if (clickedWall) {
                this.selectedObject = clickedWall;
            } else if (clickedZone) {
                this.selectedObject = clickedZone;
            } else {
                this.selectedObject = null;
            }
        } else {
            // Place object
            const snapped = this.snapToGrid(pos.x, pos.y);
            this.addObject(snapped.x, snapped.y, this.selectedTool);
        }
        
        this.render();
    }
    
    handleMouseMove(e) {
        const pos = this.getMousePos(e);
        
        if (this.isPanning) {
            this.panX = e.clientX - this.panStart.x;
            this.panY = e.clientY - this.panStart.y;
            this.render();
            return;
        }
        
        if (this.isDrawingWall && this.currentWall) {
            const snapped = this.snapToGrid(pos.x, pos.y);
            this.currentWall.x2 = snapped.x;
            this.currentWall.y2 = snapped.y;
            this.render();
        } else if (this.isDrawingZone && this.currentZone && this.zoneStart) {
            const snapped = this.snapToGrid(pos.x, pos.y);
            this.currentZone.x = Math.min(this.zoneStart.x, snapped.x);
            this.currentZone.y = Math.min(this.zoneStart.y, snapped.y);
            this.currentZone.width = Math.abs(snapped.x - this.zoneStart.x);
            this.currentZone.height = Math.abs(snapped.y - this.zoneStart.y);
            this.render();
        } else if (this.isDragging && this.selectedObject && this.selectedObject.type !== 'wall') {
            const snapped = this.snapToGrid(pos.x - this.dragOffset.x, pos.y - this.dragOffset.y);
            this.selectedObject.x = snapped.x;
            this.selectedObject.y = snapped.y;
            this.render();
        }
    }
    
    handleMouseUp(e) {
        if (this.isPanning) {
            this.isPanning = false;
            this.canvas.style.cursor = 'default';
            return;
        }
        
        if (this.isDrawingWall && this.currentWall) {
            // Only add wall if it has length
            const length = Math.sqrt(
                Math.pow(this.currentWall.x2 - this.currentWall.x1, 2) +
                Math.pow(this.currentWall.y2 - this.currentWall.y1, 2)
            );
            
            if (length > this.gridSize / 2) {
                this.walls.push({
                    ...this.currentWall,
                    type: 'wall',
                    thickness: 8
                });
                this.saveHistory();
            }
            
            this.isDrawingWall = false;
            this.wallStart = null;
            this.currentWall = null;
        }
        
        if (this.isDrawingZone && this.currentZone) {
            // Only add zone if it has area
            if (this.currentZone.width > this.gridSize && this.currentZone.height > this.gridSize) {
                this.zones.push({
                    ...this.currentZone,
                    type: 'zone',
                    label: `Room-${this.zones.length + 1}`,
                    id: Date.now()
                });
                this.saveHistory();
            }
            
            this.isDrawingZone = false;
            this.zoneStart = null;
            this.currentZone = null;
        }
        
        if (this.isDragging) {
            this.isDragging = false;
            this.canvas.style.cursor = 'default';
            this.saveHistory();
        }
        
        this.render();
    }
    
    handleWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newZoom = Math.max(0.1, Math.min(5, this.zoom * delta));
        
        // Zoom towards mouse position
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        this.panX = mouseX - (mouseX - this.panX) * (newZoom / this.zoom);
        this.panY = mouseY - (mouseY - this.panY) * (newZoom / this.zoom);
        this.zoom = newZoom;
        
        this.render();
    }
    
    handleKeyDown(e) {
        if (e.key === 'Delete' && this.selectedObject) {
            this.deleteSelected();
        } else if (e.ctrlKey && e.key === 'z') {
            this.undo();
        }
    }
    
    handleTouchStart(e) {
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.handleMouseDown({ clientX: touch.clientX, clientY: touch.clientY, button: 0 });
        }
    }
    
    handleTouchMove(e) {
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.handleMouseMove({ clientX: touch.clientX, clientY: touch.clientY });
        }
    }
    
    handleTouchEnd(e) {
        this.handleMouseUp({});
    }
    
    selectTool(tool) {
        this.selectedTool = tool;
        this.selectedObject = null;
        
        // Update UI
        document.querySelectorAll('.map-tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`[data-tool="${tool}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        this.render();
    }
    
    addObject(x, y, type) {
        const obj = {
            id: Date.now() + Math.random(),
            x: x,
            y: y,
            type: type,
            label: this.generateLabel(type),
            size: 40,
            rotation: 0
        };
        
        this.objects.push(obj);
        this.selectedObject = obj;
        this.saveHistory();
        this.render();
    }
    
    generateLabel(type) {
        const count = this.objects.filter(o => o.type === type).length + 1;
        const labels = {
            camera: 'CAM',
            door: 'DOOR',
            soldier: 'NSG',
            zone: 'ZONE'
        };
        return `${labels[type] || type.toUpperCase()}-${count}`;
    }
    
    findObjectAt(x, y) {
        for (let i = this.objects.length - 1; i >= 0; i--) {
            const obj = this.objects[i];
            const distance = Math.sqrt(Math.pow(x - obj.x, 2) + Math.pow(y - obj.y, 2));
            if (distance <= obj.size / 2) {
                return obj;
            }
        }
        return null;
    }
    
    findWallAt(x, y) {
        for (let i = this.walls.length - 1; i >= 0; i--) {
            const wall = this.walls[i];
            const dist = this.pointToLineDistance(x, y, wall.x1, wall.y1, wall.x2, wall.y2);
            if (dist <= wall.thickness) {
                return wall;
            }
        }
        return null;
    }
    
    findZoneAt(x, y) {
        for (let i = this.zones.length - 1; i >= 0; i--) {
            const zone = this.zones[i];
            if (x >= zone.x && x <= zone.x + zone.width &&
                y >= zone.y && y <= zone.y + zone.height) {
                return zone;
            }
        }
        return null;
    }
    
    pointToLineDistance(px, py, x1, y1, x2, y2) {
        const A = px - x1;
        const B = py - y1;
        const C = x2 - x1;
        const D = y2 - y1;
        
        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        let param = -1;
        
        if (lenSq !== 0) param = dot / lenSq;
        
        let xx, yy;
        
        if (param < 0) {
            xx = x1;
            yy = y1;
        } else if (param > 1) {
            xx = x2;
            yy = y2;
        } else {
            xx = x1 + param * C;
            yy = y1 + param * D;
        }
        
        const dx = px - xx;
        const dy = py - yy;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    deleteSelected() {
        if (!this.selectedObject) return;
        
        if (this.selectedObject.type === 'wall') {
            const index = this.walls.indexOf(this.selectedObject);
            if (index > -1) this.walls.splice(index, 1);
        } else if (this.selectedObject.type === 'zone') {
            const index = this.zones.indexOf(this.selectedObject);
            if (index > -1) this.zones.splice(index, 1);
        } else {
            const index = this.objects.indexOf(this.selectedObject);
            if (index > -1) this.objects.splice(index, 1);
        }
        
        this.selectedObject = null;
        this.saveHistory();
        this.render();
    }
    
    clearAll() {
        this.walls = [];
        this.zones = [];
        this.objects = [];
        this.selectedObject = null;
        this.saveHistory();
        this.render();
    }
    
    resetView() {
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.render();
    }
    
    saveHistory() {
        const state = {
            walls: JSON.parse(JSON.stringify(this.walls)),
            zones: JSON.parse(JSON.stringify(this.zones)),
            objects: JSON.parse(JSON.stringify(this.objects))
        };
        
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(state);
        this.historyIndex++;
        
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
    }
    
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            const state = this.history[this.historyIndex];
            this.walls = JSON.parse(JSON.stringify(state.walls));
            this.zones = JSON.parse(JSON.stringify(state.zones || []));
            this.objects = JSON.parse(JSON.stringify(state.objects));
            this.selectedObject = null;
            this.render();
        }
    }
    
    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            const state = this.history[this.historyIndex];
            this.walls = JSON.parse(JSON.stringify(state.walls));
            this.zones = JSON.parse(JSON.stringify(state.zones || []));
            this.objects = JSON.parse(JSON.stringify(state.objects));
            this.selectedObject = null;
            this.render();
        }
    }
    
    render() {
        this.ctx.save();
        
        // Clear canvas
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Apply zoom and pan
        this.ctx.translate(this.panX, this.panY);
        this.ctx.scale(this.zoom, this.zoom);
        
        // Draw grid
        this.drawGrid();
        
        // Draw layout image if loaded
        if (this.layoutImage) {
            this.ctx.globalAlpha = 0.5;
            this.ctx.drawImage(this.layoutImage, 0, 0);
            this.ctx.globalAlpha = 1;
        }
        
        // Draw zones (rooms/areas)
        this.zones.forEach(zone => this.drawZone(zone));
        
        // Draw current zone being drawn
        if (this.currentZone && this.currentZone.width > 0 && this.currentZone.height > 0) {
            this.drawZone(this.currentZone, true);
        }
        
        // Draw walls
        this.walls.forEach(wall => this.drawWall(wall));
        
        // Draw current wall being drawn
        if (this.currentWall) {
            this.drawWall(this.currentWall, true);
        }
        
        // Draw objects
        this.objects.forEach(obj => this.drawObject(obj));
        
        // Draw terrorist location if tracking is enabled
        if (this.trackingEnabled) {
            this.drawTerroristLocation();
        }
        
        this.ctx.restore();
    }
    
    drawGrid() {
        const startX = Math.floor(-this.panX / this.zoom / this.gridSize) * this.gridSize;
        const startY = Math.floor(-this.panY / this.zoom / this.gridSize) * this.gridSize;
        const endX = startX + (this.canvas.width / this.zoom) + this.gridSize;
        const endY = startY + (this.canvas.height / this.zoom) + this.gridSize;
        
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 0.5 / this.zoom;
        
        // Draw grid lines
        for (let x = startX; x < endX; x += this.gridSize) {
            const isMajor = x % (this.gridSize * 5) === 0;
            this.ctx.strokeStyle = isMajor ? this.colors.gridMajor : this.colors.grid;
            this.ctx.lineWidth = isMajor ? 1 / this.zoom : 0.5 / this.zoom;
            
            this.ctx.beginPath();
            this.ctx.moveTo(x, startY);
            this.ctx.lineTo(x, endY);
            this.ctx.stroke();
        }
        
        for (let y = startY; y < endY; y += this.gridSize) {
            const isMajor = y % (this.gridSize * 5) === 0;
            this.ctx.strokestyle = isMajor ? this.colors.gridMajor : this.colors.grid;
            this.ctx.lineWidth = isMajor ? 1 / this.zoom : 0.5 / this.zoom;
            
            this.ctx.beginPath();
            this.ctx.moveTo(startX, y);
            this.ctx.lineTo(endX, y);
            this.ctx.stroke();
        }
    }
    
    drawZone(zone, isPreview = false) {
        const isSelected = zone === this.selectedObject;
        
        // Draw filled rectangle for room/zone
        this.ctx.fillStyle = isPreview ? 'rgba(59, 130, 246, 0.1)' : 
                             isSelected ? 'rgba(251, 191, 36, 0.1)' : 'rgba(100, 116, 139, 0.08)';
        this.ctx.fillRect(zone.x, zone.y, zone.width, zone.height);
        
        // Draw border
        this.ctx.strokeStyle = isPreview ? this.colors.wallActive : 
                               isSelected ? this.colors.selected : this.colors.wall;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(zone.x, zone.y, zone.width, zone.height);
        
        // Draw label
        if (zone.label && !isPreview) {
            this.ctx.fillStyle = this.colors.text;
            this.ctx.font = '14px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(zone.label, zone.x + zone.width / 2, zone.y + zone.height / 2);
        }
        
        // Draw resize handles if selected
        if (isSelected) {
            const handleSize = 6;
            this.ctx.fillStyle = this.colors.selected;
            // Corners
            this.ctx.fillRect(zone.x - handleSize/2, zone.y - handleSize/2, handleSize, handleSize);
            this.ctx.fillRect(zone.x + zone.width - handleSize/2, zone.y - handleSize/2, handleSize, handleSize);
            this.ctx.fillRect(zone.x - handleSize/2, zone.y + zone.height - handleSize/2, handleSize, handleSize);
            this.ctx.fillRect(zone.x + zone.width - handleSize/2, zone.y + zone.height - handleSize/2, handleSize, handleSize);
        }
    }
    
    drawWall(wall, isPreview = false) {
        const isSelected = wall === this.selectedObject;
        
        this.ctx.strokeStyle = isPreview ? this.colors.wallActive : 
                               isSelected ? this.colors.selected : this.colors.wall;
        this.ctx.lineWidth = wall.thickness || 8;
        this.ctx.lineCap = 'square';
        
        this.ctx.beginPath();
        this.ctx.moveTo(wall.x1, wall.y1);
        this.ctx.lineTo(wall.x2, wall.y2);
        this.ctx.stroke();
        
        // Draw handles if selected
        if (isSelected) {
            this.ctx.fillStyle = this.colors.selected;
            this.ctx.fillRect(wall.x1 - 4, wall.y1 - 4, 8, 8);
            this.ctx.fillRect(wall.x2 - 4, wall.y2 - 4, 8, 8);
        }
    }
    
    drawObject(obj) {
        const isSelected = obj === this.selectedObject;
        
        this.ctx.save();
        this.ctx.translate(obj.x, obj.y);
        if (obj.rotation) this.ctx.rotate(obj.rotation * Math.PI / 180);
        
        const size = obj.size;
        const halfSize = size / 2;
        
        // Draw based on type
        switch (obj.type) {
            case 'camera':
                this.ctx.fillStyle = this.colors.camera;
                this.ctx.beginPath();
                this.ctx.arc(0, 0, halfSize, 0, Math.PI * 2);
                this.ctx.fill();
                
                // Camera icon
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = `${size * 0.6}px Arial`;
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText('📷', 0, 0);
                break;
                
            case 'door':
                this.ctx.fillStyle = this.colors.door;
                this.ctx.fillRect(-halfSize, -halfSize, size, size);
                
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = `${size * 0.5}px Arial`;
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText('🚪', 0, 0);
                break;
                
            case 'soldier':
                this.ctx.fillStyle = this.colors.soldier;
                this.ctx.beginPath();
                this.ctx.arc(0, 0, halfSize, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = `${size * 0.5}px Arial`;
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText('🎖️', 0, 0);
                break;
                
            case 'zone':
                this.ctx.strokeStyle = this.colors.zone;
                this.ctx.lineWidth = 3;
                this.ctx.strokeRect(-halfSize, -halfSize, size, size);
                break;
        }
        
        // Draw label
        if (obj.label) {
            this.ctx.fillStyle = this.colors.text;
            this.ctx.font = '12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(obj.label, 0, halfSize + 15);
        }
        
        // Draw selection indicator
        if (isSelected) {
            this.ctx.strokeStyle = this.colors.selected;
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([5, 5]);
            this.ctx.strokeRect(-halfSize - 5, -halfSize - 5, size + 10, size + 10);
            this.ctx.setLineDash([]);
        }
        
        this.ctx.restore();
    }
    
    async uploadLayout(file) {
        try {
            console.log('Uploading floor plan:', file.name);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', file);
            formData.append('name', 'Floor Plan');
            formData.append('width_meters', '50');
            formData.append('height_meters', '50');
            
            // Upload to server
            const response = await fetch('/api/map/layouts/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Upload failed:', response.status, errorText);
                throw new Error(`Upload failed: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Floor plan uploaded successfully:', result);
            
            // Reload background image from server
            await this.loadBackgroundImage();
            
            alert('Floor plan uploaded successfully!');
        } catch (error) {
            console.error('Error uploading floor plan:', error);
            alert('Failed to upload floor plan: ' + error.message);
        }
    }
    
    exportMap() {
        return {
            walls: this.walls,
            objects: this.objects,
            zoom: this.zoom,
            panX: this.panX,
            panY: this.panY
        };
    }
    
    importMap(data) {
        this.walls = data.walls || [];
        this.objects = data.objects || [];
        if (data.zoom) this.zoom = data.zoom;
        if (data.panX !== undefined) this.panX = data.panX;
        if (data.panY !== undefined) this.panY = data.panY;
        this.saveHistory();
        this.render();
    }
    
    async loadBackgroundImage() {
        try {
            console.log('Loading background image...');
            const response = await fetch('/api/map/layouts/');
            
            if (!response.ok) {
                console.log('No map layout found, status:', response.status);
                return;
            }
            
            const layouts = await response.json();
            console.log('Layouts received:', layouts);
            
            if (!layouts || layouts.length === 0) {
                console.log('No map layouts available');
                return;
            }
            
            // Get the most recent layout
            const layout = layouts[layouts.length - 1];
            console.log('Using layout:', layout);
            
            if (layout.image) {
                const img = new Image();
                img.onload = () => {
                    this.layoutImage = img;
                    this.render();
                    console.log('Background image loaded successfully:', layout.image);
                };
                img.onerror = () => {
                    console.error('Failed to load background image:', layout.image);
                };
                img.src = layout.image;
            }
        } catch (error) {
            console.error('Error loading background image:', error);
        }
    }
    
    refreshBackground() {
        this.loadBackgroundImage();
    }
    
    async loadLayoutById(layoutId) {
        try {
            console.log('Loading layout by ID:', layoutId);
            const response = await fetch(`/api/map/layouts/${layoutId}/`);
            
            if (!response.ok) {
                console.error('Failed to load layout:', response.status);
                alert('Failed to load floor plan');
                return;
            }
            
            const layout = await response.json();
            console.log('Layout loaded:', layout);
            
            if (layout.image) {
                const img = new Image();
                img.onload = () => {
                    this.layoutImage = img;
                    this.render();
                    console.log('Layout image loaded successfully:', layout.image);
                };
                img.onerror = () => {
                    console.error('Failed to load layout image:', layout.image);
                };
                img.src = layout.image;
            }
        } catch (error) {
            console.error('Error loading layout:', error);
            alert('Error loading floor plan: ' + error.message);
        }
    }
}

// Initialize when DOM is ready
let mapEditor = null;

function initMapEditor() {
    const canvas = document.getElementById('architectureMapCanvas');
    if (canvas) {
        mapEditor = new ArchitectureMapEditor('architectureMapCanvas', document.getElementById('mapEditorContainer'));
    }
}

// Auto-initialize if canvas exists
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMapEditor);
} else {
    initMapEditor();
}

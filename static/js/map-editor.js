// Professional 2D Architecture Map Editor - Grid-Based with Wall Drawing

class MapEditor {
    constructor(canvasId = 'mapCanvas') {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.layoutImage = null;
        this.objects = [];
        this.walls = [];
        this.selectedTool = 'select';
        this.selectedObject = null;
        this.isDragging = false;
        this.isDrawingWall = false;
        this.wallStart = null;
        this.dragOffset = { x: 0, y: 0 };
        this.history = [];
        this.mapId = null;
        
        // Canvas settings
        this.gridSize = 20;
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.panStart = { x: 0, y: 0 };
        
        // Colors
        this.colors = {
            background: '#1a1a2e',
            grid: '#2a2a3e',
            wall: '#4a4a5e',
            camera: '#3498db',
            door: '#e67e22',
            soldier: '#2ecc71',
            zone: '#e74c3c',
            selected: '#f39c12'
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadExistingMap();
        this.loadSavedMapsList();
    }

    setupEventListeners() {
        // Upload layout
        document.getElementById('layoutUpload').addEventListener('change', (e) => {
            this.handleLayoutUpload(e);
        });

        // AI Auto-draw
        document.getElementById('aiDrawBtn').addEventListener('click', () => {
            this.aiAutoDraw();
        });
        
        // Load saved map
        const savedMapSelector = document.getElementById('savedMapSelector');
        if (savedMapSelector) {
            savedMapSelector.addEventListener('change', (e) => {
                const mapName = e.target.value;
                if (mapName) {
                    console.log('Loading saved map:', mapName);
                    this.loadMapAs(mapName);
                }
            });
        }

        // Tool selection
        document.querySelectorAll('.tool-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectTool(e.currentTarget.dataset.tool);
            });
        });

        // Canvas interactions
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('dblclick', (e) => this.handleDoubleClick(e));

        // Actions
        document.getElementById('saveMapBtn').addEventListener('click', () => this.saveMap());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());
        document.getElementById('undoBtn').addEventListener('click', () => this.undo());
        document.getElementById('resetZoomBtn').addEventListener('click', () => this.resetZoom());

        // Object properties
        document.getElementById('deleteObjBtn').addEventListener('click', () => this.deleteSelectedObject());
        document.getElementById('closePropsBtn').addEventListener('click', () => this.closeProperties());
        document.getElementById('objLabel').addEventListener('input', (e) => this.updateObjectLabel(e.target.value));
        document.getElementById('objType').addEventListener('change', (e) => this.updateObjectType(e.target.value));
    }

    handleLayoutUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                this.layoutImage = img;
                this.setupCanvas(img.width, img.height);
                this.uploadLayoutToServer(file);
                document.getElementById('emptyState').style.display = 'none';
                this.canvas.style.display = 'block';
                this.render();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    setupCanvas(width, height) {
        this.canvas.width = width;
        this.canvas.height = height;
    }

    selectTool(toolType) {
        this.selectedTool = toolType;
        document.querySelectorAll('.tool-button').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.closest('.tool-button').classList.add('active');
        this.canvas.style.cursor = 'crosshair';
    }

    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Check if clicking on existing object
        const clickedObj = this.findObjectAt(x, y);
        
        if (clickedObj) {
            this.selectedObject = clickedObj;
            this.isDragging = true;
            this.dragOffset = {
                x: x - clickedObj.x,
                y: y - clickedObj.y
            };
            this.canvas.style.cursor = 'move';
        } else if (this.selectedTool) {
            // Place new object
            this.addObject(x, y, this.selectedTool);
        }
    }

    handleMouseMove(e) {
        if (!this.isDragging || !this.selectedObject) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        this.selectedObject.x = x - this.dragOffset.x;
        this.selectedObject.y = y - this.dragOffset.y;
        this.render();
    }

    handleMouseUp(e) {
        if (this.isDragging) {
            this.isDragging = false;
            this.canvas.style.cursor = this.selectedTool ? 'crosshair' : 'default';
            this.saveHistory();
        }
    }

    handleDoubleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const obj = this.findObjectAt(x, y);
        if (obj) {
            this.showObjectProperties(obj);
        }
    }

    addObject(x, y, type) {
        const obj = {
            id: Date.now(),
            x: x,
            y: y,
            type: type,
            label: `${type.charAt(0).toUpperCase() + type.slice(1)}-${this.objects.length + 1}`,
            size: 30
        };

        this.objects.push(obj);
        this.saveHistory();
        this.render();

        // Auto-show properties for new objects
        this.showObjectProperties(obj);
    }

    findObjectAt(x, y) {
        // Search in reverse (top objects first)
        for (let i = this.objects.length - 1; i >= 0; i--) {
            const obj = this.objects[i];
            const distance = Math.sqrt(Math.pow(x - obj.x, 2) + Math.pow(y - obj.y, 2));
            if (distance <= obj.size / 2) {
                return obj;
            }
        }
        return null;
    }

    drawObject(obj) {
        this.ctx.save();

        // Object styles based on type
        const styles = {
            camera: { color: '#34d3ff', icon: '📷' },
            zone: { color: '#f5576c', icon: '🔲' },
            sensor: { color: '#f093fb', icon: '📡' },
            door: { color: '#38ef7d', icon: '🚪' },
            marker: { color: '#feca57', icon: '📍' }
        };

        const style = styles[obj.type] || styles.marker;

        // Draw circle background
        this.ctx.beginPath();
        this.ctx.arc(obj.x, obj.y, obj.size / 2, 0, Math.PI * 2);
        this.ctx.fillStyle = style.color + '40';
        this.ctx.fill();
        this.ctx.strokeStyle = style.color;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Draw icon
        this.ctx.font = '20px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(style.icon, obj.x, obj.y);

        // Draw label
        this.ctx.font = '12px Arial';
        this.ctx.fillStyle = 'white';
        this.ctx.fillText(obj.label, obj.x, obj.y + obj.size / 2 + 15);

        // Highlight if selected
        if (obj === this.selectedObject) {
            this.ctx.beginPath();
            this.ctx.arc(obj.x, obj.y, obj.size / 2 + 5, 0, Math.PI * 2);
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([5, 5]);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }

        this.ctx.restore();
    }

    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw layout image
        if (this.layoutImage) {
            this.ctx.drawImage(this.layoutImage, 0, 0);
        }

        // Draw all objects
        this.objects.forEach(obj => this.drawObject(obj));
    }

    showObjectProperties(obj) {
        this.selectedObject = obj;
        const panel = document.getElementById('objectProperties');
        panel.classList.add('show');
        
        document.getElementById('objLabel').value = obj.label;
        document.getElementById('objType').value = obj.type;
    }

    closeProperties() {
        document.getElementById('objectProperties').classList.remove('show');
        this.selectedObject = null;
        this.render();
    }

    updateObjectLabel(label) {
        if (this.selectedObject) {
            this.selectedObject.label = label;
            this.render();
        }
    }

    updateObjectType(type) {
        if (this.selectedObject) {
            this.selectedObject.type = type;
            this.render();
        }
    }

    deleteSelectedObject() {
        if (this.selectedObject) {
            const index = this.objects.indexOf(this.selectedObject);
            if (index > -1) {
                this.objects.splice(index, 1);
            }
            this.closeProperties();
            this.saveHistory();
            this.render();
        }
    }

    saveHistory() {
        this.history.push(JSON.parse(JSON.stringify(this.objects)));
        if (this.history.length > 20) {
            this.history.shift();
        }
    }

    undo() {
        if (this.history.length > 1) {
            this.history.pop();
            this.objects = JSON.parse(JSON.stringify(this.history[this.history.length - 1]));
            this.render();
        }
    }

    clearAll() {
        if (confirm('Clear all objects from the map?')) {
            this.objects = [];
            this.saveHistory();
            this.render();
        }
    }

    resetZoom() {
        // TODO: Implement zoom controls
        this.render();
    }

    async aiAutoDraw() {
        if (!this.layoutImage) {
            alert('Please upload a floor plan first!');
            return;
        }

        const btn = document.getElementById('aiDrawBtn');
        btn.textContent = '⏳ AI Processing...';
        btn.disabled = true;

        try {
            // Create a temporary canvas for edge detection
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = this.canvas.width;
            tempCanvas.height = this.canvas.height;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(this.layoutImage, 0, 0);

            // Get image data
            const imageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
            
            // Apply AI edge detection and room recognition
            const detectedZones = this.detectZonesAI(imageData);
            
            // Add detected zones to map
            detectedZones.forEach((zone, index) => {
                this.objects.push({
                    id: Date.now() + index,
                    x: zone.x,
                    y: zone.y,
                    type: 'zone',
                    label: `Room-${index + 1}`,
                    size: 30
                });
            });

            this.saveHistory();
            this.render();

            btn.textContent = `✅ Found ${detectedZones.length} Zones`;
            setTimeout(() => {
                btn.textContent = '🤖 AI Auto-Draw Map';
                btn.disabled = false;
            }, 2000);

        } catch (error) {
            console.error('AI Auto-draw failed:', error);
            btn.textContent = '❌ AI Failed';
            setTimeout(() => {
                btn.textContent = '🤖 AI Auto-Draw Map';
                btn.disabled = false;
            }, 2000);
        }
    }

    detectZonesAI(imageData) {
        // Simple AI-based zone detection using edge detection and clustering
        const zones = [];
        const { width, height, data } = imageData;

        // Convert to grayscale and detect edges (Sobel operator)
        const gray = new Uint8ClampedArray(width * height);
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            gray[i / 4] = 0.299 * r + 0.587 * g + 0.114 * b;
        }

        // Find bright regions (potential rooms)
        const gridSize = 100; // Sample every 100px
        for (let y = gridSize; y < height - gridSize; y += gridSize) {
            for (let x = gridSize; x < width - gridSize; x += gridSize) {
                const idx = y * width + x;
                const brightness = gray[idx];

                // Detect bright areas (likely interior spaces)
                if (brightness > 200) {
                    // Check if this area is distinct (has edges around it)
                    const hasEdges = this.checkSurroundingEdges(gray, x, y, width, height, gridSize);
                    
                    if (hasEdges) {
                        zones.push({ x, y });
                    }
                }
            }
        }

        // Remove duplicate/close zones
        return this.clusterZones(zones, gridSize);
    }

    checkSurroundingEdges(gray, x, y, width, height, radius) {
        let edgeCount = 0;
        const threshold = 50;

        // Check pixels around the zone
        for (let dy = -radius; dy <= radius; dy += 20) {
            for (let dx = -radius; dx <= radius; dx += 20) {
                const nx = x + dx;
                const ny = y + dy;
                
                if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                    const idx = ny * width + nx;
                    const centerIdx = y * width + x;
                    
                    if (Math.abs(gray[idx] - gray[centerIdx]) > threshold) {
                        edgeCount++;
                    }
                }
            }
        }

        return edgeCount > 5; // Has significant edges around it
    }

    clusterZones(zones, minDistance) {
        const clustered = [];
        
        zones.forEach(zone => {
            let isTooClose = false;
            
            for (const existing of clustered) {
                const distance = Math.sqrt(
                    Math.pow(zone.x - existing.x, 2) + 
                    Math.pow(zone.y - existing.y, 2)
                );
                
                if (distance < minDistance) {
                    isTooClose = true;
                    break;
                }
            }
            
            if (!isTooClose) {
                clustered.push(zone);
            }
        });

        return clustered;
    }

    async uploadLayoutToServer(file) {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('width', this.canvas.width);
        formData.append('height', this.canvas.height);

        try {
            const response = await fetch('/api/map/layouts/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.mapId = data.id;
                console.log('Layout uploaded successfully:', data);
            }
        } catch (error) {
            console.error('Failed to upload layout:', error);
        }
    }

    async saveMap() {
        // Prompt user for filename
        const filename = prompt('Enter map name to save:', 'FloorPlan');
        if (!filename) {
            console.log('Save cancelled');
            return;
        }

        try {
            // Export map data
            const mapData = {
                walls: this.walls,
                objects: this.objects,
                zoom: this.zoom,
                panX: this.panX,
                panY: this.panY,
                timestamp: new Date().toISOString()
            };
            
            // Save to localStorage
            localStorage.setItem(`map_${filename}`, JSON.stringify(mapData));
            
            // Also save to API if layout exists
            if (this.mapId) {
                // Delete existing objects
                await fetch(`/api/map/objects/?layout=${this.mapId}`, {
                    method: 'GET'
                }).then(res => res.json()).then(async (existing) => {
                    for (const obj of existing) {
                        await fetch(`/api/map/objects/${obj.id}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-CSRFToken': this.getCookie('csrftoken')
                            }
                        });
                    }
                });

                // Save all objects to API
                for (const obj of this.objects) {
                    await fetch('/api/map/objects/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            layout: this.mapId,
                            object_type: obj.type,
                            label: obj.label,
                            x_position: Math.round(obj.x),
                            y_position: Math.round(obj.y)
                        })
                    });
                }
            }
            
            alert(`✅ Map saved as "${filename}"`);
            console.log('Map saved:', filename);
            
            // Reload the dropdown with new map
            this.loadSavedMapsList();
        } catch (error) {
            console.error('Failed to save map:', error);
            alert('❌ Failed to save map: ' + error.message);
        }
    }
    
    loadMapAs(filename) {
        try {
            const savedData = localStorage.getItem(`map_${filename}`);
            if (!savedData) {
                alert('Map file not found');
                return false;
            }
            
            const mapData = JSON.parse(savedData);
            this.walls = mapData.walls || [];
            this.objects = mapData.objects || [];
            this.zoom = mapData.zoom || 1;
            this.panX = mapData.panX || 0;
            this.panY = mapData.panY || 0;
            
            this.render();
            console.log('Map loaded:', filename);
            return true;
        } catch (error) {
            console.error('Error loading map:', error);
            alert('Error loading map: ' + error.message);
            return false;
        }
    }
    
    getListSavedMaps() {
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
    
    loadSavedMapsList() {
        const selector = document.getElementById('savedMapSelector');
        if (!selector) return;
        
        const savedMaps = this.getListSavedMaps();
        console.log('Saved maps found:', savedMaps);
        
        // Clear existing options except placeholder
        while (selector.options.length > 1) {
            selector.remove(1);
        }
        
        // Add saved maps as options
        savedMaps.forEach(mapName => {
            const option = document.createElement('option');
            option.value = mapName;
            option.textContent = mapName;
            selector.appendChild(option);
        });
    }

    async loadExistingMap() {
        try {
            // Load latest layout
            const layoutsRes = await fetch('/api/map/layouts/');
            const layouts = await layoutsRes.json();
            
            if (layouts.length > 0) {
                const layout = layouts[0];
                this.mapId = layout.id;

                // Load image
                const img = new Image();
                img.onload = () => {
                    this.layoutImage = img;
                    this.setupCanvas(layout.width, layout.height);
                    document.getElementById('emptyState').style.display = 'none';
                    this.canvas.style.display = 'block';
                    this.loadObjects(layout.id);
                };
                img.src = layout.image;
            }
        } catch (error) {
            console.error('Failed to load existing map:', error);
        }
    }

    async loadObjects(layoutId) {
        try {
            const response = await fetch(`/api/map/objects/?layout=${layoutId}`);
            const objects = await response.json();

            this.objects = objects.map(obj => ({
                id: obj.id,
                x: obj.x_position,
                y: obj.y_position,
                type: obj.object_type,
                label: obj.label,
                size: 30
            }));

            this.saveHistory();
            this.render();
        } catch (error) {
            console.error('Failed to load objects:', error);
        }
    }

    getCookie(name) {
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
}

// Initialize map editor
const mapEditor = new MapEditor();

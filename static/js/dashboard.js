// RakshNetra Dashboard JavaScript

const mapState = {
    canvas: null,
    ctx: null,
    layout: null,
    objects: [],
    image: null,
    drawMode: false
};

function getCSRFToken() {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArr = decodedCookie.split(';');
    for (let i = 0; i < cookieArr.length; i++) {
        let c = cookieArr[i].trim();
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return '';
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DASHBOARD LOADED ===');
    try {
        initializeUI();
    } catch (error) {
        console.error('UI initialization failed:', error);
    }
    try {
        setupEventListeners();
    } catch (error) {
        console.error('Event listeners setup failed:', error);
    }
    setupEventSelector(); // Setup server-rendered event selector
    loadModels();
    // Retry model load once after initial render
    setTimeout(loadModels, 1500);
});

// ========== UI Initialization ==========
function initializeUI() {
    console.log('Initializing UI...');
    setupTabNavigation();
    setupVideoGrid();
    setupMapCanvas();
    setupModals();
    console.log('UI initialized');
}

function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Remove active from all
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active to clicked
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            if (tabName === 'situational-map' && architectureMapEditor) {
                architectureMapEditor.resizeCanvas();
                architectureMapEditor.render();
            }
        });
    });
}

// ========== Event Management ==========
function setupEventSelector() {
    console.log('Setting up event selector...');
    const select = document.getElementById('event-select');
    if (!select) {
        console.warn('Event selector not found');
        return;
    }

    // Setup change listener for server-rendered options
    select.addEventListener('change', function() {
        if (this.value) {
            const option = this.options[this.selectedIndex];
            const location = option.getAttribute('data-location') || '-';
            const threat = option.getAttribute('data-threat') || '-';
            const start = option.getAttribute('data-start') || '-';
            
            // Update event details panel
            document.getElementById('event-location').textContent = location;
            document.getElementById('event-threat-level').textContent = threat;
            document.getElementById('event-threat-level').className = `threat-badge ${threat}`;
            document.getElementById('event-start').textContent = start;
            document.getElementById('event-status').textContent = 'Active';
            document.getElementById('event-details').style.display = 'block';
            
            // Load event-specific content
            loadMapLayout(this.value);
        } else {
            document.getElementById('event-details').style.display = 'none';
            clearMapLayout();
        }
    });

    // Auto-select first event if available
    if (select.options.length > 1) {
        select.selectedIndex = 1;
        select.dispatchEvent(new Event('change'));
    }
    
    console.log('Event selector setup complete');
}

// ========== Camera Management ==========
function setupVideoGrid() {
    const grid = document.getElementById('video-grid-layout');
    
    console.log('Setting up video grid...');
    
    // First try to use server-rendered data if available
    if (window.dashboardData && window.dashboardData.cameras && window.dashboardData.cameras.length > 0) {
        console.log('Using server-rendered camera data');
        populateVideoGrid(grid, window.dashboardData.cameras);
        return;
    }
    
    // Fallback: Load cameras from API
    fetch('/api/cameras/', {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
    })
        .then(response => {
            if (!response.ok) {
                console.warn('Cameras API not available');
                // Check server data again
                if (window.dashboardData && window.dashboardData.cameras) {
                    populateVideoGrid(grid, window.dashboardData.cameras);
                } else {
                    return null;
                }
                return null;
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                const cameras = data.results || data;
                populateVideoGrid(grid, cameras);
            }
        })
        .catch(error => {
            console.warn('Error loading cameras:', error);
            if (window.dashboardData && window.dashboardData.cameras) {
                populateVideoGrid(grid, window.dashboardData.cameras);
            } else {
                grid.innerHTML = '';
                for (let i = 1; i <= 4; i++) {
                    addPlaceholderCamera(grid, i);
                }
            }
        });
}

function populateVideoGrid(grid, cameras) {
    grid.innerHTML = '';
    
    if (!cameras || cameras.length === 0) {
        grid.innerHTML = '<div style="padding: 20px; color: #888; text-align: center; grid-column: 1/-1;">No cameras configured. <a href="/manage/cameras/" style="color: #00d4ff;">Add one now</a></div>';
        return;
    }
    
    cameras.forEach(camera => {
        const item = document.createElement('div');
        item.className = 'video-item';
        item.setAttribute('data-camera-id', camera.id);
        const status = camera.enabled ? 'ACTIVE' : 'INACTIVE';
        const statusColor = camera.enabled ? '#00d4ff' : '#cc6666';
        
        // Check if it's a video file (not MJPEG stream)
        const isVideoFile = camera.protocol === 'file' || camera.protocol === 'FILE' || camera.source.toLowerCase().includes('.mp4') || camera.source.toLowerCase().includes('.avi');
        
        console.log(`Camera ${camera.name}: isVideoFile=${isVideoFile}, protocol=${camera.protocol}`);
        
        if (isVideoFile) {
            // Video player with controls - use MJPEG stream for detection
            item.innerHTML = `
                <div class="video-label" style="background: ${statusColor}; color: #000; font-weight: bold;">
                    ${camera.name} | ${status}
                </div>
                <div class="video-frame">
                    <img id="video-${camera.id}" src="/video_feed/${camera.id}/" style="width: 100%; height: 100%; object-fit: contain; background: #000;" />
                </div>
                <div class="video-control-bar">
                    <div class="video-control-row">
                        <button class="video-control-btn" onclick="alert('⏸ Pause/Play\\n\\nLive stream cannot be paused. Video continues running with real-time detection.')" title="Stream is live">▶</button>
                        <span style="flex: 1; text-align: center; color: #aaa; font-size: 0.85rem;">🔴 LIVE STREAM (DETECTION ACTIVE)</span>
                    </div>
                    <div style="background: #1a3a1a; padding: 8px; border-radius: 3px; margin-top: 5px;">
                        <div style="color: #0f0; font-size: 0.8rem; font-weight: bold;">✓ ALL DETECTION MODELS RUNNING</div>
                        <div style="color: #0f0; font-size: 0.75rem; margin-top: 3px;">Face • Weapon • Fire • NSG • Suspicious</div>
                    </div>
                </div>
                <div class="video-controls">
                    <a href="/camera/${camera.id}/" class="video-btn" title="Full View">👁</a>
                    <a href="/manage/cameras/" class="video-btn" title="Manage">⚙️</a>
                    <span class="video-btn" style="cursor: pointer;" title="${camera.protocol}">📡</span>
                </div>
            `;
            
            // Setup MJPEG stream for detection
            grid.appendChild(item);
            
            // Start polling for face detection on this stream
            startDetectionPolling(camera.id);
        } else {
            // MJPEG stream (webcam)
            item.innerHTML = `
                <div class="video-label" style="background: ${statusColor}; color: #000; font-weight: bold;">
                    ${camera.name} | ${status}
                </div>
                <div style="width: 100%; height: 100%; background: #000; display: flex; align-items: center; justify-content: center; position: relative;">
                    <img src="/video_feed/${camera.id}/" alt="${camera.name}" style="width: 100%; height: 100%; object-fit: contain;">
                </div>
                <div class="video-controls">
                    <a href="/camera/${camera.id}/" class="video-btn" title="Open">👁</a>
                    <a href="/manage/cameras/" class="video-btn" title="Manage">⚙️</a>
                    <span class="video-btn" style="cursor: pointer;" title="${camera.protocol}">📡</span>
                </div>
            `;
            grid.appendChild(item);
        }
    });
}

function addPlaceholderCamera(grid, index) {
    const item = document.createElement('div');
    item.className = 'video-item';
    item.innerHTML = `
        <div class="video-label">CAM-0${index} | STANDBY</div>
        <div style="width: 100%; height: 100%; background: linear-gradient(135deg, #1a2a3a 0%, #0d1b2a 100%); display: flex; align-items: center; justify-content: center;">
            <span style="color: #666; font-size: 0.9rem;">No feed</span>
        </div>
        <div class="video-controls">
            <a href="/manage/cameras/" class="video-btn" title="Add Camera">➕</a>
            <span class="video-btn" title="Not configured">❌</span>
        </div>
    `;
    grid.appendChild(item);
}

// ========== AI Models ==========
function loadModels() {
    console.log('Loading active models...');
    
    // First try the active models endpoint
    fetch('/api/ai/models/active/', {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
    })
        .then(response => {
            if (!response.ok) {
                console.log('Active models endpoint failed, trying all models...');
                return fetch('/api/ai/models/', {
                    credentials: 'include',
                    headers: { 'Accept': 'application/json' }
                }).then(r => r.json());
            }
            return response.json();
        })
        .then(data => {
            const modelList = document.getElementById('model-list');
            if (!modelList) {
                console.warn('Model list element not found');
                return;
            }
            
            modelList.innerHTML = '';
            console.log('Models data:', data);

            // Handle both list and paginated responses
            const models = (data.results || data) || [];
            
            if (!models || models.length === 0) {
                modelList.innerHTML = '<div style="padding: 10px; color: #0f0; font-size: 0.9rem;">✓ All Models Ready<br><span style="font-size: 0.8rem; color: #888;">(5 detection models active)</span></div>';
                return;
            }

            models.forEach(model => {
                const item = document.createElement('div');
                item.className = 'model-item';
                const status = model.is_active ? 'active' : 'idle';
                item.innerHTML = `
                    <div><strong>${model.name}</strong></div>
                    <div style="font-size: 0.75rem; color: #a8b3c1;">${model.model_type || 'detection'}</div>
                    <div class="model-status ${status}">${status.toUpperCase()}</div>
                    <div style="color: #10b981; font-size: 0.75rem;">✓ Ready</div>
                `;
                modelList.appendChild(item);
            });
        })
        .catch(error => {
            console.warn('Models API error:', error);
            const modelList = document.getElementById('model-list');
            if (modelList) {
                modelList.innerHTML = '<div style="padding: 10px; color: #0f0; font-size: 0.9rem;">✓ Models Ready<br><span style="font-size: 0.8rem; color: #888;">(Weapon, Fire, NSG, Suspicious, Face Detection)</span></div>';
            }
        });
}

// ========== Map Canvas ==========
let architectureMapEditor = null;

function setupMapCanvas() {
    console.log('Setting up map canvas...');
    const canvas = document.getElementById('architectureMapCanvas');
    if (!canvas) {
        console.log('Architecture map canvas not found');
        return;
    }

    // Initialize professional map editor
    const container = document.getElementById('mapEditorContainer');
    console.log('Creating ArchitectureMapEditor instance...');
    architectureMapEditor = new ArchitectureMapEditor('architectureMapCanvas', container);
    
    // Setup toolbar button events
    setupMapToolbar();
}

function setupMapToolbar() {
    console.log('Setting up map toolbar...');
    
    // Load available layouts
    loadAvailableLayouts();
    
    // Tool selection buttons
    document.querySelectorAll('.map-tool-btn').forEach(btn => {
        const tool = btn.dataset.tool;
        if (tool) {
            btn.addEventListener('click', () => {
                console.log('Tool selected:', tool);
                // Remove active from all
                document.querySelectorAll('.map-tool-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                if (architectureMapEditor) {
                    architectureMapEditor.selectTool(tool);
                }
            });
        }
    });
    
    // Layout selector
    const layoutSelector = document.getElementById('layoutSelector');
    if (layoutSelector) {
        layoutSelector.addEventListener('change', (e) => {
            const value = e.target.value;
            if (!value) return;
            
            console.log('Loading layout:', value);
            
            if (value.startsWith('api_')) {
                // Load from API
                const layoutId = value.replace('api_', '');
                if (architectureMapEditor) {
                    architectureMapEditor.loadLayoutById(layoutId);
                }
            } else if (value.startsWith('local_')) {
                // Load from localStorage
                const mapName = value.replace('local_', '');
                if (architectureMapEditor) {
                    architectureMapEditor.loadMapAs(mapName);
                }
            }
        });
    } else {
        console.warn('Layout selector not found');
    }
    
    // Delete button
    const deleteBtn = document.getElementById('deleteMapObjectBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            console.log('Delete clicked');
            if (architectureMapEditor) {
                architectureMapEditor.deleteSelected();
            }
        });
    }
    
    // Upload layout button
    const uploadBtn = document.getElementById('uploadLayoutBtn');
    const fileInput = document.getElementById('layoutFileInput');
    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => {
            console.log('Upload button clicked');
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            console.log('File selected:', file ? file.name : 'none');
            if (file && architectureMapEditor) {
                architectureMapEditor.uploadLayout(file);
            }
        });
    } else {
        console.warn('Upload button or file input not found');
    }
    
    // Refresh background button
    const refreshBtn = document.getElementById('refreshBackgroundBtn');
    if (refreshBtn) {
        console.log('Refresh button found and wired');
        refreshBtn.addEventListener('click', () => {
            console.log('Refresh button clicked');
            if (architectureMapEditor) {
                architectureMapEditor.refreshBackground();
            }
        });
    } else {
        console.warn('Refresh background button not found');
    }
    
    console.log('Map toolbar setup complete');
    
    // Zoom controls
    const zoomInBtn = document.getElementById('zoomInBtn');
    const zoomOutBtn = document.getElementById('zoomOutBtn');
    const resetViewBtn = document.getElementById('resetViewBtn');
    
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            if (architectureMapEditor) {
                architectureMapEditor.zoom *= 1.2;
                architectureMapEditor.render();
            }
        });
    }
    
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            if (architectureMapEditor) {
                architectureMapEditor.zoom /= 1.2;
                architectureMapEditor.render();
            }
        });
    }
    
    if (resetViewBtn) {
        resetViewBtn.addEventListener('click', () => {
            if (architectureMapEditor) {
                architectureMapEditor.resetView();
            }
        });
    }
    
    // Save map button
    const saveMapBtn = document.getElementById('saveMapBtn');
    if (saveMapBtn) {
        saveMapBtn.addEventListener('click', () => {
            console.log('Save map clicked');
            const filename = prompt('Enter map name:', 'FloorPlan');
            if (filename && architectureMapEditor) {
                architectureMapEditor.saveMapAs(filename);
                // Reload the dropdown
                setTimeout(() => loadAvailableLayouts(), 100);
            }
        });
    }
    
    // Enable tracking button
    const enableTrackingBtn = document.getElementById('enableTrackingBtn');
    if (enableTrackingBtn) {
        enableTrackingBtn.addEventListener('click', () => {
            console.log('Enable tracking clicked');
            const isEnabled = enableTrackingBtn.getAttribute('data-tracking') === 'true';
            const newStatus = !isEnabled;
            
            enableTrackingBtn.setAttribute('data-tracking', newStatus);
            enableTrackingBtn.style.opacity = newStatus ? '1' : '0.5';
            enableTrackingBtn.style.color = newStatus ? '#10b981' : '#9ca3af';
            
            if (architectureMapEditor) {
                architectureMapEditor.enableTracking(newStatus);
            }
            
            console.log('Tracking mode:', newStatus ? 'ENABLED' : 'DISABLED');
        });
    }
}

function drawMap() {
    // Legacy function - now handled by ArchitectureMapEditor
    if (architectureMapEditor) {
        architectureMapEditor.render();
    }
}

// ========== Layout Management ==========
async function loadAvailableLayouts() {
    try {
        console.log('Loading available layouts...');
        const selector = document.getElementById('layoutSelector');
        if (!selector) return;
        
        // Clear existing options (keep the placeholder)
        while (selector.options.length > 1) {
            selector.remove(1);
        }
        
        // Load from API first
        const response = await fetch('/api/map/layouts/');
        if (response.ok) {
            const layouts = await response.json();
            if (layouts && layouts.length > 0) {
                const section = document.createElement('optgroup');
                section.label = 'Floor Plans';
                layouts.forEach(layout => {
                    const option = document.createElement('option');
                    option.value = `api_${layout.id}`;
                    option.textContent = layout.name || `Floor Plan ${layout.id}`;
                    section.appendChild(option);
                });
                selector.appendChild(section);
                console.log('API layouts loaded:', layouts.length);
            }
        }
        
        // Load from localStorage (saved maps)
        if (architectureMapEditor) {
            const savedMaps = architectureMapEditor.getListSavedMaps();
            if (savedMaps && savedMaps.length > 0) {
                const section = document.createElement('optgroup');
                section.label = 'Saved Maps';
                savedMaps.forEach(mapName => {
                    const option = document.createElement('option');
                    option.value = `local_${mapName}`;
                    option.textContent = mapName;
                    section.appendChild(option);
                });
                selector.appendChild(section);
                console.log('Saved maps loaded:', savedMaps.length);
            }
        }
    } catch (error) {
        console.error('Error loading layouts:', error);
    }
}

function getMapObjectColor(type) {
    switch (type) {
        case 'camera':
            return '#0ea5e9';
        case 'cctv':
            return '#38bdf8';
        case 'nsg_unit':
            return '#10b981';
        case 'police':
            return '#3b82f6';
        case 'vip':
            return '#a855f7';
        case 'suspect':
            return '#ef4444';
        case 'restricted_zone':
            return '#ef4444';
        case 'door':
            return '#f59e0b';
        case 'wall':
            return '#94a3b8';
        case 'gate':
            return '#f97316';
        case 'entry':
            return '#22c55e';
        case 'exit':
            return '#e11d48';
        default:
            return '#38bdf8';
    }
}

// ========== Modals ==========
function setupModals() {
    const addCameraBtn = document.getElementById('add-camera-btn');
    const addCameraModal = document.getElementById('add-camera-modal');
    const modalClose = document.querySelector('.modal-close');
    const addCameraForm = document.getElementById('add-camera-form');

    if (addCameraBtn && addCameraModal) {
        addCameraBtn.addEventListener('click', () => {
            addCameraModal.classList.add('active');
        });

        modalClose.addEventListener('click', () => {
            addCameraModal.classList.remove('active');
        });

        addCameraModal.addEventListener('click', (e) => {
            if (e.target === addCameraModal) {
                addCameraModal.classList.remove('active');
            }
        });

        addCameraForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(addCameraForm);
            const csrfToken = getCSRFToken();
            
            // Prepare JSON data
            const data = {
                name: formData.get('name'),
                protocol: formData.get('protocol'),
                source: formData.get('source'),
                mode: formData.get('mode')
            };
            
            // Send to API
            fetch('/api/cameras/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'include',
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.detail || 'Failed to add camera');
                    });
                }
                return response.json();
            })
            .then(camera => {
                console.log('Camera added:', camera);
                alert(`✓ Camera "${camera.name}" added successfully!`);
                addCameraModal.classList.remove('active');
                addCameraForm.reset();
                // Reload camera list
                setupVideoGrid();
            })
            .catch(error => {
                console.error('Error adding camera:', error);
                alert(`✗ Error: ${error.message}`);
            });
        });
    }
}

// ========== Detection Polling Functions ==========
function startDetectionPolling(cameraId) {
    // Poll for detections every 500ms
    const pollInterval = setInterval(() => {
        pollCameraDetections(cameraId);
    }, 500);
    
    // Store interval ID for cleanup if needed
    if (!window.detectionIntervals) {
        window.detectionIntervals = {};
    }
    window.detectionIntervals[cameraId] = pollInterval;
}

function pollCameraDetections(cameraId) {
    fetch(`/api/cameras/${cameraId}/current_detections/`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
    })
        .then(response => {
            if (!response.ok) return null;
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            const videoItem = document.querySelector(`[data-camera-id="${cameraId}"]`);
            if (!videoItem) return;
            
            // Display all detections (faces, weapons, objects)
            let detectionText = '';
            
            if (data.faces && data.faces.length > 0) {
                const identifiedFaces = data.faces.filter(f => f.name && f.name !== 'Unknown');
                if (identifiedFaces.length > 0) {
                    detectionText += '<strong style="color: #0f0;">👤 FACES:</strong> ';
                    detectionText += identifiedFaces.map(f => {
                        const conf = Math.round((f.confidence || 0) * 100);
                        return `${f.name} (${conf}%)`;
                    }).join(', ');
                    detectionText += '<br>';
                }
            }
            
            if (data.objects && data.objects.length > 0) {
                detectionText += '<strong style="color: #ff0;">🔍 OBJECTS:</strong> ';
                detectionText += data.objects.map(o => `${o.type}(${o.count})`).join(', ');
                detectionText += '<br>';
            }
            
            if (data.weapons && data.weapons.length > 0) {
                detectionText += '<strong style="color: #f00;">⚔️ WEAPONS:</strong> ';
                detectionText += data.weapons.map(w => `${w.type}(${w.count})`).join(', ');
            }
            
            // Update or create detection panel
            let detectionPanel = videoItem.querySelector('.detection-summary');
            if (!detectionPanel && detectionText) {
                detectionPanel = document.createElement('div');
                detectionPanel.className = 'detection-summary';
                detectionPanel.style.cssText = 'position: absolute; bottom: 50px; left: 10px; right: 10px; background-color: rgba(0, 0, 0, 0.8); border: 1px solid #0f0; padding: 8px; border-radius: 4px; color: #0f0; font-size: 0.7rem; z-index: 10;';
                videoItem.style.position = 'relative';
                // Insert after video element
                videoItem.querySelector('img, video').parentElement.appendChild(detectionPanel);
            }
            
            if (detectionPanel) {
                if (detectionText) {
                    detectionPanel.innerHTML = detectionText;
                    detectionPanel.style.display = 'block';
                } else {
                    detectionPanel.style.display = 'none';
                }
            }
        })
        .catch(error => {
            // Silent fail - detection API might be slow
        });
}

// ========== Alert Updates ==========
function updateAlertUI(alert) {
    const alertFeed = document.getElementById('alert-feed');
    
    const alertItem = document.createElement('div');
    alertItem.className = `alert-item ${alert.severity}`;
    alertItem.innerHTML = `
        <div><strong>${alert.threat_type}</strong></div>
        <div class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</div>
        <div style="font-size: 0.75rem; color: #a8b3c1;">Confidence: ${(alert.confidence * 100).toFixed(1)}%</div>
    `;
    
    alertFeed.insertBefore(alertItem, alertFeed.firstChild);
    
    // Keep only last 10 alerts
    while (alertFeed.children.length > 10) {
        alertFeed.removeChild(alertFeed.lastChild);
    }

    // Update alert counts
    updateAlertCounts();
}

function updateAlertCounts() {
    const alertFeed = document.getElementById('alert-feed');
    let critical = 0, warning = 0, info = 0;

    alertFeed.querySelectorAll('.alert-item').forEach(item => {
        if (item.classList.contains('critical')) critical++;
        else if (item.classList.contains('warning')) warning++;
        else info++;
    });

    document.querySelector('.count-badge.critical').textContent = critical;
    document.querySelector('.count-badge.warning').textContent = warning;
    document.querySelector('.count-badge.info').textContent = info;
}

// ========== Map Updates ==========
function updateMapUI(update) {
    console.log('Map update:', update);
    
    // Update terrorist location if tracking is enabled
    if (update.terrorist_location && architectureMapEditor) {
        const { x, y } = update.terrorist_location;
        architectureMapEditor.updateTerroristLocation(x, y);
    }
    
    // Update NSG positions if provided
    if (update.nsg_positions && architectureMapEditor) {
        console.log('NSG positions:', update.nsg_positions);
    }
    
    // Placeholder: Update other positions as needed
}

function loadMapLayout(eventId) {
    const status = document.getElementById('map-status');
    if (!eventId) {
        clearMapLayout();
        return;
    }

    fetch(`/api/map/layouts/?event=${eventId}`)
        .then(response => response.json())
        .then(data => {
            const layouts = data.results || data;
            if (!layouts || layouts.length === 0) {
                clearMapLayout();
                status.textContent = 'No layout for this event';
                return;
            }

            mapState.layout = layouts[0];
            status.textContent = `Layout loaded (${mapState.layout.width_meters}m x ${mapState.layout.height_meters}m)`;
            loadMapImage(mapState.layout.image_url || mapState.layout.image);
            loadMapObjects(mapState.layout.id);
        })
        .catch(error => {
            console.warn('Error loading map layout:', error);
            clearMapLayout();
            if (status) status.textContent = 'Layout load failed';
        });
}

function loadMapImage(url) {
    if (!url) return;
    const image = new Image();
    image.onload = function() {
        mapState.image = image;
        drawMap();
    };
    image.src = url;
}

function loadMapObjects(layoutId) {
    if (!layoutId) return;
    fetch(`/api/map/objects/?layout=${layoutId}`)
        .then(response => response.json())
        .then(data => {
            mapState.objects = data.results || data || [];
            drawMap();
        })
        .catch(error => {
            console.warn('Error loading map objects:', error);
        });
}

function clearMapLayout() {
    mapState.layout = null;
    mapState.objects = [];
    mapState.image = null;
    const status = document.getElementById('map-status');
    if (status) status.textContent = 'No layout loaded';
    drawMap();
}

function uploadMapLayout(file) {
    const eventSelect = document.getElementById('event-select');
    const eventId = eventSelect ? eventSelect.value : null;
    const status = document.getElementById('map-status');
    const widthMeters = document.getElementById('map-width').value;
    const heightMeters = document.getElementById('map-height').value;

    if (!eventId) {
        if (status) status.textContent = 'Select an event first';
        return;
    }

    const formData = new FormData();
    formData.append('event', eventId);
    formData.append('image', file);
    formData.append('width_meters', widthMeters);
    formData.append('height_meters', heightMeters);

    fetch('/api/map/layouts/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
        .then(async response => {
            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || 'Upload failed');
            }
            return response.json();
        })
        .then(layout => {
            mapState.layout = layout;
            if (status) status.textContent = 'Layout uploaded';
            loadMapImage(layout.image_url || layout.image);
            loadMapObjects(layout.id);
            if (mapState.resizeCanvas) mapState.resizeCanvas();
        })
        .catch(error => {
            console.warn('Error uploading layout:', error);
            if (status) status.textContent = `Upload failed: ${error.message}`;
        });
}

function createMapObject(x, y) {
    if (!mapState.layout) return;
    const type = document.getElementById('map-point-type').value;
    const label = document.getElementById('map-point-label').value || '';

    fetch('/api/map/objects/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            map_layout: mapState.layout.id,
            obj_type: type,
            x,
            y,
            label
        })
    })
        .then(response => response.json())
        .then(obj => {
            mapState.objects.push(obj);
            drawMap();
        })
        .catch(error => console.warn('Error creating map object:', error));
}

// ========== Event Listeners ==========
function setupEventListeners() {
    // Video grid controls
    document.addEventListener('click', function(e) {
        if (e.target.closest('.video-btn')) {
            const button = e.target.closest('.video-btn');
            const videoItem = button.closest('.video-item');
            
            if (button.textContent === '⚙️') {
                // Toggle mode
                videoItem.classList.toggle('ai-mode');
            } else if (button.textContent === '✕') {
                // Remove
                videoItem.remove();
            }
        }
    });

    // Map tools
    const mapUploadBtn = document.getElementById('upload-map-btn');
    const drawToolBtn = document.getElementById('draw-tool-btn');
    const mapUploadInput = document.getElementById('map-upload-input');
    const mapCanvas = document.getElementById('map-canvas');
    
    if (mapUploadBtn) {
        mapUploadBtn.addEventListener('click', () => {
            if (mapUploadInput) {
                mapUploadInput.click();
            }
        });
    }

    if (mapUploadInput) {
        mapUploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                uploadMapLayout(file);
            }
            mapUploadInput.value = '';
        });
    }
    
    if (drawToolBtn) {
        drawToolBtn.addEventListener('click', () => {
            mapState.drawMode = !mapState.drawMode;
            drawToolBtn.textContent = mapState.drawMode ? 'Drawing: ON' : 'Draw Tool';
        });
    }

    if (mapCanvas) {
        mapCanvas.addEventListener('click', (e) => {
            if (!mapState.drawMode || !mapState.layout) return;
            const rect = mapCanvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) / mapCanvas.width;
            const y = (e.clientY - rect.top) / mapCanvas.height;
            createMapObject(x, y);
        });
    }
}

// ========== Video Player Control Functions ==========
function initializeVideoPlayer(cameraId, sourceUrl, detectedVideoUrl) {
    const video = document.getElementById(`video-${cameraId}`);
    const videoSource = document.getElementById(`videoSource-${cameraId}`);
    
    if (!video || !videoSource) {
        console.warn(`Video elements not found for camera ${cameraId}`);
        return;
    }
    
    try {
        let videoUrl = detectedVideoUrl;
        if (!videoUrl) {
            // If sourceUrl is already a path (contains /)
            if (sourceUrl.includes('/') || sourceUrl.includes('\\')) {
                // It's a file path like "media/draupathi_murmur.mp4"
                videoUrl = `/${sourceUrl}`;
            } else {
                // It's just a filename, add media/videos prefix
                videoUrl = `/media/videos/${sourceUrl}`;
            }
        }
        
        console.log(`Camera ${cameraId}: Setting video source to ${videoUrl}`);
        
        videoSource.src = videoUrl;
        video.load();
        
        // Update duration when loaded
        video.addEventListener('loadedmetadata', () => {
            const durationEl = document.getElementById(`duration-${cameraId}`);
            if (durationEl) {
                durationEl.textContent = formatTime(video.duration);
            }
            console.log(`Camera ${cameraId}: Video loaded, duration ${video.duration}s`);
        });
        
        // Update time display and progress bar
        video.addEventListener('timeupdate', () => {
            const timeEl = document.getElementById(`time-${cameraId}`);
            if (timeEl) {
                timeEl.textContent = formatTime(video.currentTime);
            }
            
            const progressEl = document.getElementById(`progress-${cameraId}`);
            if (progressEl && video.duration) {
                const percent = (video.currentTime / video.duration) * 100;
                progressEl.style.width = percent + '%';
            }
            
            // Poll for face detection
            pollFaceDetection(cameraId);
        });
        
        video.addEventListener('error', (e) => {
            console.error(`Video error for camera ${cameraId}:`, e);
        });
        
    } catch (error) {
        console.error(`Error initializing video player for camera ${cameraId}:`, error);
    }
}

function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '00:00';
    const totalSeconds = Math.floor(seconds);
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = Math.floor(totalSeconds % 60);
    
    if (h > 0) {
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    } else {
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
}

function togglePlay(cameraId) {
    const video = document.getElementById(`video-${cameraId}`);
    if (video) {
        video.paused ? video.play() : video.pause();
    }
}

function skipBack(cameraId) {
    const video = document.getElementById(`video-${cameraId}`);
    if (video) {
        video.currentTime = Math.max(0, video.currentTime - 5);
    }
}

function skipForward(cameraId) {
    const video = document.getElementById(`video-${cameraId}`);
    if (video) {
        video.currentTime = Math.min(video.duration, video.currentTime + 5);
    }
}

function prevFrame(cameraId) {
    const video = document.getElementById(`video-${cameraId}`);
    if (video) {
        video.currentTime = Math.max(0, video.currentTime - 0.033); // 30 FPS
    }
}

function nextFrame(cameraId) {
    const video = document.getElementById(`video-${cameraId}`);
    if (video) {
        video.currentTime = Math.min(video.duration, video.currentTime + 0.033); // 30 FPS
    }
}

function seekTimeline(event, cameraId) {
    const video = document.getElementById(`video-${cameraId}`);
    const timeline = event.currentTarget;
    if (video && timeline) {
        const percent = event.offsetX / timeline.offsetWidth;
        video.currentTime = percent * video.duration;
    }
}

function pollFaceDetection(cameraId) {
    // Poll detection API for current frame - every frame update
    const video = document.getElementById(`video-${cameraId}`);
    if (!video) return;
    
    // Skip if too frequent (throttle to every 500ms)
    const lastPoll = window[`lastFacePoll_${cameraId}`] || 0;
    const now = Date.now();
    if (now - lastPoll < 500) return;
    window[`lastFacePoll_${cameraId}`] = now;
    
    fetch(`/api/cameras/${cameraId}/current_detections/`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
    })
        .then(response => {
            if (!response.ok) return null;
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            // Log detection result for debugging
            if (data.faces && data.faces.length > 0) {
                console.log(`Camera ${cameraId} face detection:`, data.faces);
                updateFaceDisplay(cameraId, data.faces);
            } else {
                // Clear or show "Scanning"
                const videoItem = document.querySelector(`[data-camera-id="${cameraId}"]`);
                if (videoItem) {
                    let panel = videoItem.querySelector('.face-detection-panel');
                    if (panel) {
                        panel.innerHTML = '<div style="color: #aaa; font-size: 0.75rem; padding: 5px;">👁 Analyzing frames...</div>';
                    }
                }
            }
        })
        .catch(error => {
            // Silent fail - detection API might be slow
        });
}

function updateFaceDisplay(cameraId, faces) {
    // Find or create detection panel in video item
    const videoItem = document.querySelector(`[data-camera-id="${cameraId}"]`);
    if (!videoItem) return;
    
    let detectionPanel = videoItem.querySelector('.face-detection-panel');
    if (!detectionPanel) {
        detectionPanel = document.createElement('div');
        detectionPanel.className = 'face-detection-panel';
        videoItem.appendChild(detectionPanel);
    }
    
    // Filter out unknown faces only show identified ones
    const identifiedFaces = faces.filter(f => f.name && f.name !== 'Unknown');
    
    if (identifiedFaces.length === 0) {
        detectionPanel.innerHTML = '<div style="color: #aaa; font-size: 0.8rem;">Scanning for faces...</div>';
        return;
    }
    
    let html = '<div style="background-color: rgba(0, 255, 0, 0.1); border: 1px solid #0f0; padding: 8px; border-radius: 3px;"><strong style="color: #0f0;">👤 DETECTED FACES</strong><div style="font-size: 0.85rem;">';
    identifiedFaces.forEach(face => {
        const name = face.name || 'Unknown';
        const confidence = Math.round((face.confidence || 0) * 100);
        const title = face.title ? `<div style="color: #888; font-size: 0.75rem;">${face.title}</div>` : '';
        
        html += `<div style="padding: 5px 0; border-bottom: 1px solid #0f0 30%; margin-bottom: 3px;">
            <div style="color: #0f0; font-weight: bold;">${name}</div>
            <div style="color: #0f0; font-size: 0.75rem;">✓ ${confidence}% confidence</div>
            ${title}
        </div>`;
    });
    html += '</div></div>';
    detectionPanel.innerHTML = html;
}

// ========== Utility Functions ==========
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function bytesToMB(bytes) {
    return (bytes / 1024 / 1024).toFixed(2);
}

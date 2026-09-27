# 3D Visualization Integration Guide
This guide explains how to integrate Three.js 3D visualizations into Mengo-Hub for interactive learning diagrams.

---
## Architecture Overview
### Backend (Flask)
- Stores 3D model metadata in `system_settings` table
- `/api/premium/3d/models` - GET list, POST create
- `/api/premium/3d/models/:id` - GET, PUT, DELETE
- `/api/premium/3d/models/:id/download` - Download model file

### Frontend (HTML/JS)
- Uses Three.js for WebGL rendering
- Loads models from endpoints
- Interactive controls (rotate, zoom, pan)
- Real-time annotations

---
## Setting Up 3D Models
### 1. Model File Formats Supported
- **GLTF/GLB** (.gltf, .glb) - Recommended, supports animations
- **OBJ** (.obj) - Simple, widely compatible
- **JSON** (.json) - Custom format for procedural models

### 2. Upload 3D Models
Create models in Blender, export to GLTF, then register:
```bash
# Store model files in public/models/
cp cell-diagram.glb public/models/
cp human-skeleton.glb public/models/

# Register in database via API
curl -X POST https://mengo-hub.local/api/premium/3d/models \
  -H "Authorization: Bearer AdminToken" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "Animal Cell",
    "description": "Interactive 3D model of an animal cell showing organelles",
    "subject": "Biology",
    "topic": "Cell Structure",
    "model_url": "/models/cell-diagram.glb",
    "model_type": "gltf",
    "difficulty": "intermediate",
    "annotations": {
      "nucleus": "Control center of the cell",
      "mitochondria": "Power house - produces energy",
      "ribosome": "Protein synthesis factory",
      "endoplasmic_reticulum": "Protein and lipid processing"
    }
  }'
```

### 3. Database Entry
Models stored in `system_settings` table:
```json
{
  "setting_key": "3d_models",
  "setting_value": [
    {
      "id": "model_001",
      "name": "Animal Cell",
      "subject": "Biology",
      "url": "/models/cell-diagram.glb",
      "type": "gltf",
      "annotations": {
        "nucleus": "Description..."
      }
    }
  ]
}
```
---
## Frontend Integration (Three.js)
### Basic HTML Setup
```html
<!DOCTYPE html>
<html>
<head>
    <title>3D Biology Diagrams</title>
    <style>
        #canvas-container {
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .controls {
            padding: 10px;
            background: #f5f5f5;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .control-btn {
            padding: 8px 12px;
            margin-right: 5px;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .annotations {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px;
            border-radius: 4px;
            max-width: 250px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>3D Cell Structure Visualization</h1>
    
    <div class="controls">
        <button class="control-btn" onclick="resetView()">Reset View</button>
        <button class="control-btn" onclick="toggleWireframe()">Wireframe</button>
        <button class="control-btn" onclick="toggleAnnotations()">Show Labels</button>
        <button class="control-btn" onclick="rotateModel()">Auto-Rotate</button>
    </div>
    
    <div id="canvas-container"></div>
    <div id="annotations" class="annotations"></div>

    <!-- THREE.JS LIBRARIES -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/controls/OrbitControls.js"></script>

    <script>
        // THREE.JS SETUP
        let scene, camera, renderer, controls, model;
        let wireframeMode = false;
        let showAnnotations = true;
        const annotationsData = {};

        function initThreeJS() {
            // Scene setup
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f0f0);

            // Camera
            camera = new THREE.PerspectiveCamera(
                75,
                document.getElementById('canvas-container').clientWidth / 
                document.getElementById('canvas-container').clientHeight,
                0.1,
                1000
            );
            camera.position.set(0, 2, 5);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(
                document.getElementById('canvas-container').clientWidth,
                document.getElementById('canvas-container').clientHeight
            );
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.autoRotate = false;
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 10, 7);
            scene.add(directionalLight);

            // Start animation loop
            animate();
        }

        async function loadModel(modelUrl, annotations = {}) {
            const loader = new THREE.GLTFLoader();
            
            loader.load(modelUrl, (gltf) => {
                model = gltf.scene;
                scene.add(model);
                
                // Center and scale model
                const box = new THREE.Box3().setFromObject(model);
                const center = box.getCenter(new THREE.Vector3());
                model.position.sub(center);
                
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 5 / maxDim;
                model.scale.multiplyScalar(scale);
                
                annotationsData = annotations;
            }, 
            undefined, 
            (error) => {
                console.error('Error loading model:', error);
            });
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        function resetView() {
            camera.position.set(0, 2, 5);
            controls.target.set(0, 0, 0);
            controls.update();
        }

        function toggleWireframe() {
            wireframeMode = !wireframeMode;
            model.traverse(child => {
                if (child.isMesh) {
                    child.material.wireframe = wireframeMode;
                }
            });
        }

        function toggleAnnotations() {
            showAnnotations = !showAnnotations;
            const annDiv = document.getElementById('annotations');
            if (showAnnotations && Object.keys(annotationsData).length > 0) {
                annDiv.innerHTML = Object.entries(annotationsData)
                    .map(([key, val]) => `<strong>${key}:</strong> ${val}`)
                    .join('<br>');
                annDiv.style.display = 'block';
            } else {
                annDiv.style.display = 'none';
            }
        }

        function rotateModel() {
            controls.autoRotate = !controls.autoRotate;
        }

        // ON PAGE LOAD
        window.addEventListener('load', async () => {
            initThreeJS();
            
            // Fetch and load model
            const modelId = new URLSearchParams(window.location.search).get('model_id') || 'model_001';
            const res = await fetch(`/api/premium/3d/models/${modelId}`);
            const data = await res.json();
            
            if (data.success) {
                await loadModel(data.model.url, data.model.annotations);
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            const width = document.getElementById('canvas-container').clientWidth;
            const height = document.getElementById('canvas-container').clientHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        });
    </script>
</body>
</html>
```

---
## API Endpoints
### List All 3D Models
```bash
curl https://mengo-hub.local/api/premium/3d/models \
  -H "Authorization: Bearer Token"
# Response
{
  "success": true,
  "models": [
    {
      "id": "model_001",
      "name": "Animal Cell",
      "subject": "Biology",
      "description": "Interactive 3D model...",
      "url": "/models/cell-diagram.glb",
      "type": "gltf"
    }
  ]
}
```

### Get Specific Model
```bash
curl https://mengo-hub.local/api/premium/3d/models/model_001 \
  -H "Authorization: Bearer Token"

# Response
{
  "success": true,
  "model": {
    "id": "model_001",
    "name": "Animal Cell",
    "url": "/models/cell-diagram.glb",
    "type": "gltf",
    "annotations": {
      "nucleus": "Control center",
      "mitochondria": "Powerhouse"
    },
    "difficulty": "intermediate"
  }
}
```

### Create New Model
```bash
curl -X POST https://mengo-hub.local/api/premium/3d/models \
  -H "Authorization: Bearer AdminToken" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "A000",
    "model_name": "Human Skeleton",
    "description": "Complete skeletal system",
    "subject": "Biology",
    "topic": "Anatomy",
    "model_url": "/models/skeleton.glb",
    "model_type": "gltf",
    "annotations": {
      "femur": "Longest bone in body",
      "skull": "Protects brain"
    }
  }'
```

### Update Model
```bash
curl -X PUT https://mengo-hub.local/api/premium/3d/models/model_001 \
  -H "Authorization: Bearer AdminToken" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "A000",
    "annotations": {
      "nucleus": "Updated description"
    }
  }'
```

### Delete Model
```bash
curl -X DELETE https://mengo-hub.local/api/premium/3d/models/model_001 \
  -H "Authorization: Bearer AdminToken" \
  -H "Content-Type: application/json" \
  -d '{"admin_id": "A000"}'
```

---
## Creating 3D Models in Blender
1. **Model creation**:
   - Use Blender for modeling
   - Add materials and textures
   - Add annotations via custom properties

2. **Export to GLTF**:
   - File → Export → glTF (.glb/.gltf)
   - Keep textures included
   - Enable compression if file large

3. **Upload to Mengo-Hub**:
   - Place in `public/models/` directory
   - Register via admin panel
   - Test display in Three.js viewer

---
## Browser Compatibility
- Chrome 90+: Full support
- Firefox 88+: Full support
- Safari 14+: Full support
- Edge 90+: Full support

---
## Performance Tip
1. **Model optimization**:
   - Keep polygon count < 100K
   - Use efficient textures (PNG/WEBP)
   - Bake lighting when possible

2. **Loading**:
   - Show loading spinner while fetching
   - Cache models in browser (localStorage)
   - Use progressive loading for complex scenes

3. **Rendering**:
   - Use LOD (Level of Detail) for complex models
   - Implement frustum culling
   - Throttle animation on low-end devices

---
## Example Models
**Biology**:
- Animal Cell (organelles)
- Plant Cell structure
- DNA double helix
- Human skeleton
- Heart anatomy

**Physics**:
- Atomic structure
- Molecular models
- Planetary system
- Wave mechanics

**Chemistry**:
- Periodic table elements
- Crystal structures
- Molecular bonding
- Reaction mechanisms

**Geography**:
- Earth layers
- Tectonic plates
- Water cycle
- Climate zones

---
## Integration with Learning Path
Link 3D models to courses:
```json
{
  "course_id": "BIO101",
  "title": "Cell Biology",
  "modules": [
    {
      "name": "Cell Structure",
      "3d_models": ["model_001", "model_002"],
      "quiz_link": "/quiz/cell-structure"
    }
  ]
}
```

---
## Support
- Three.js documentation: https://threejs.org/docs/
- Blender export: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- GLTF format: https://www.khronos.org/gltf/


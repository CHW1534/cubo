/**
 * Motor de Renderizado 3D con Three.js para el Cubo de Rubik.
 * Mantiene alineacion perfecta entre la matriz logica y los meshes 3D en 2x2, 3x3, 4x4 y 5x5.
 * Incluye animaciones fluidas por capas e indicadores direccionales.
 */

class Cube3DVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.size = 3;
        this.cubies = [];
        this.viewMode = 'front';
        this.isAnimating = false;

        this.onFaceClickCallback = null;

        // Mapa de colores estandar
        this.colorMap = {
            'white': 0xffffff,
            'yellow': 0xffd700,
            'orange': 0xff8c00,
            'red': 0xdc143c,
            'green': 0x00a86b,
            'blue': 0x4169e1,
            'internal': 0x111625
        };

        this.initScene();
        this.createCube(this.size);
        this.setupResizeObserver();
        this.setupRaycaster();
        this.animate();
    }

    initScene() {
        this.scene = new THREE.Scene();

        const width = this.container.clientWidth || 600;
        const height = this.container.clientHeight || 450;
        const aspect = width / height;

        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
        this.updateCameraPosition(width, height);

        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        this.renderer.domElement.style.position = 'absolute';
        this.renderer.domElement.style.top = '0';
        this.renderer.domElement.style.left = '0';
        this.renderer.domElement.style.width = '100%';
        this.renderer.domElement.style.height = '100%';
        this.renderer.domElement.style.outline = 'none';

        this.container.appendChild(this.renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
        this.scene.add(ambientLight);

        const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.65);
        dirLight1.position.set(12, 20, 15);
        this.scene.add(dirLight1);

        const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.45);
        dirLight2.position.set(-12, -10, -12);
        this.scene.add(dirLight2);

        this.cubeGroup = new THREE.Group();
        this.cubeGroup.rotation.set(0, 0, 0);
        this.scene.add(this.cubeGroup);

        this.isDragging = false;
        this.hasMoved = false;
        this.pointerStart = { x: 0, y: 0 };
        this.previousPointerPosition = { x: 0, y: 0 };

        const startDrag = (x, y) => {
            if (this.isAnimating) return;
            this.isDragging = true;
            this.hasMoved = false;
            this.pointerStart = { x, y };
            this.previousPointerPosition = { x, y };
        };

        const moveDrag = (x, y) => {
            if (!this.isDragging) return;
            const deltaX = x - this.previousPointerPosition.x;
            const deltaY = y - this.previousPointerPosition.y;

            if (Math.abs(x - this.pointerStart.x) > 5 || Math.abs(y - this.pointerStart.y) > 5) {
                this.hasMoved = true;
            }

            this.cubeGroup.rotation.y += deltaX * 0.008;
            this.cubeGroup.rotation.x += deltaY * 0.008;

            this.previousPointerPosition = { x, y };
        };

        const endDrag = () => {
            this.isDragging = false;
        };

        this.container.addEventListener('mousedown', (e) => startDrag(e.clientX, e.clientY));
        window.addEventListener('mousemove', (e) => moveDrag(e.clientX, e.clientY));
        window.addEventListener('mouseup', endDrag);

        this.container.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                startDrag(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: true });

        window.addEventListener('touchmove', (e) => {
            if (this.isDragging && e.touches.length === 1) {
                moveDrag(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: true });

        window.addEventListener('touchend', endDrag);
    }

    setupRaycaster() {
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        this.container.addEventListener('click', (e) => {
            if (this.hasMoved || this.isAnimating) return;

            const rect = this.container.getBoundingClientRect();
            this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            this.raycaster.setFromCamera(this.mouse, this.camera);
            const intersects = this.raycaster.intersectObjects(this.cubies);

            if (intersects.length > 0) {
                const hit = intersects[0];
                const normal = hit.face.normal.clone();
                normal.transformDirection(hit.object.matrixWorld);

                const faceName = this.getFaceFromNormal(normal);
                if (faceName && this.onFaceClickCallback) {
                    const move = e.shiftKey ? `${faceName}'` : faceName;
                    this.onFaceClickCallback(move);
                }
            }
        });
    }

    getFaceFromNormal(normal) {
        if (normal.x > 0.5) return 'R';
        if (normal.x < -0.5) return 'L';
        if (normal.y > 0.5) return 'U';
        if (normal.y < -0.5) return 'D';
        if (normal.z > 0.5) return 'F';
        if (normal.z < -0.5) return 'B';
        return null;
    }

    setOnFaceClick(callback) {
        this.onFaceClickCallback = callback;
    }

    setViewMode(mode) {
        this.viewMode = mode;
        this.resetView();
    }

    updateCameraPosition(width, height) {
        const aspect = width / height;
        const baseDist = this.size * 2.4;
        const distance = aspect < 1 ? baseDist / (aspect * 0.85) : baseDist;

        this.camera.up.set(0, 1, 0);

        if (this.viewMode === 'front') {
            this.camera.position.set(0, 0, distance * 1.45);
        } else {
            this.camera.position.set(distance * 0.45, distance * 0.35, distance * 0.82);
        }

        this.camera.lookAt(0, 0, 0);
    }

    resetView() {
        this.cubeGroup.rotation.set(0, 0, 0);
        const width = this.container.clientWidth || 600;
        const height = this.container.clientHeight || 450;
        this.updateCameraPosition(width, height);
    }

    setupResizeObserver() {
        const resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                const width = entry.contentRect.width;
                const height = entry.contentRect.height;
                if (width > 0 && height > 0) {
                    this.camera.aspect = width / height;
                    this.updateCameraPosition(width, height);
                    this.camera.updateProjectionMatrix();
                    this.renderer.setSize(width, height, false);
                }
            }
        });
        resizeObserver.observe(this.container);
    }

    createCube(size) {
        this.size = size;

        while (this.cubeGroup.children.length > 0) {
            const child = this.cubeGroup.children[0];
            this.cubeGroup.remove(child);
        }
        this.cubies = [];

        const cubieSize = 0.94;
        const spacing = 1.0;
        const offset = (size - 1) / 2;

        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                for (let z = 0; z < size; z++) {
                    const geometry = new THREE.BoxGeometry(cubieSize, cubieSize, cubieSize);
                    
                    const materials = [
                        new THREE.MeshStandardMaterial({ color: this.colorMap.red, roughness: 0.25 }),     // R
                        new THREE.MeshStandardMaterial({ color: this.colorMap.orange, roughness: 0.25 }),  // L
                        new THREE.MeshStandardMaterial({ color: this.colorMap.white, roughness: 0.25 }),   // U
                        new THREE.MeshStandardMaterial({ color: this.colorMap.yellow, roughness: 0.25 }),  // D
                        new THREE.MeshStandardMaterial({ color: this.colorMap.green, roughness: 0.25 }),   // F
                        new THREE.MeshStandardMaterial({ color: this.colorMap.blue, roughness: 0.25 })     // B
                    ];

                    const cubie = new THREE.Mesh(geometry, materials);
                    cubie.position.set((x - offset) * spacing, (y - offset) * spacing, (z - offset) * spacing);

                    cubie.userData = { gridX: x, gridY: y, gridZ: z };
                    this.cubeGroup.add(cubie);
                    this.cubies.push(cubie);
                }
            }
        }

        this.cubeGroup.rotation.set(0, 0, 0);
        const width = this.container.clientWidth || 600;
        const height = this.container.clientHeight || 450;
        this.updateCameraPosition(width, height);
    }

    /**
     * Animacion 3D fluida de giro por capas.
     */
    animateMove(move, durationMs = 420, onComplete = null) {
        if (this.isAnimating || !move) {
            if (onComplete) onComplete();
            return;
        }

        const face = move[0];
        const isPrime = move.includes("'");
        const isDouble = move.includes("2");

        const n = this.size;
        const layerCubies = [];

        this.cubies.forEach(cubie => {
            const { gridX, gridY, gridZ } = cubie.userData;
            if (face === 'U' && gridY === n - 1) layerCubies.push(cubie);
            else if (face === 'D' && gridY === 0) layerCubies.push(cubie);
            else if (face === 'L' && gridX === 0) layerCubies.push(cubie);
            else if (face === 'R' && gridX === n - 1) layerCubies.push(cubie);
            else if (face === 'F' && gridZ === n - 1) layerCubies.push(cubie);
            else if (face === 'B' && gridZ === 0) layerCubies.push(cubie);
        });

        if (layerCubies.length === 0) {
            if (onComplete) onComplete();
            return;
        }

        this.isAnimating = true;

        const pivot = new THREE.Group();
        this.cubeGroup.add(pivot);

        layerCubies.forEach(cubie => {
            pivot.add(cubie);
        });

        let angle = Math.PI / 2;
        if (isDouble) angle = Math.PI;
        
        let axis = 'y';
        if (face === 'U') { axis = 'y'; angle = isPrime ? angle : -angle; }
        else if (face === 'D') { axis = 'y'; angle = isPrime ? -angle : angle; }
        else if (face === 'L') { axis = 'x'; angle = isPrime ? -angle : angle; }
        else if (face === 'R') { axis = 'x'; angle = isPrime ? angle : -angle; }
        else if (face === 'F') { axis = 'z'; angle = isPrime ? angle : -angle; }
        else if (face === 'B') { axis = 'z'; angle = isPrime ? -angle : angle; }

        const startTime = performance.now();

        const stepAnimation = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / durationMs, 1);
            
            const easeProgress = progress < 0.5 
                ? 2 * progress * progress 
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;

            pivot.rotation[axis] = angle * easeProgress;

            if (progress < 1) {
                requestAnimationFrame(stepAnimation);
            } else {
                pivot.rotation[axis] = angle;
                pivot.updateMatrixWorld();

                const cubiesToReattach = [...pivot.children];
                cubiesToReattach.forEach(cubie => {
                    this.cubeGroup.add(cubie);
                });

                this.cubeGroup.remove(pivot);
                this.isAnimating = false;

                if (onComplete) onComplete();
            }
        };

        requestAnimationFrame(stepAnimation);
    }

    updateState(cubeState) {
        if (!cubeState || !cubeState.faces) return;
        
        if (cubeState.size !== this.size || this.cubies.length !== Math.pow(cubeState.size, 3)) {
            this.createCube(cubeState.size);
        }

        const faces = cubeState.faces;
        const n = this.size;
        const spacing = 1.0;
        const offset = (n - 1) / 2;

        this.cubies.forEach(cubie => {
            const { gridX, gridY, gridZ } = cubie.userData;

            // Re-alinear las transformaciones fisicas 3D a las coordenadas puras de la matriz logica
            cubie.rotation.set(0, 0, 0);
            cubie.position.set((gridX - offset) * spacing, (gridY - offset) * spacing, (gridZ - offset) * spacing);

            // Cara Arriba (U)
            if (gridY === n - 1) {
                const colorStr = faces.U[n - 1 - gridZ][gridX];
                cubie.material[2].color.setHex(this.colorMap[colorStr] || 0xffffff);
                cubie.material[2].needsUpdate = true;
            } else {
                cubie.material[2].color.setHex(this.colorMap.internal);
                cubie.material[2].needsUpdate = true;
            }

            // Cara Abajo (D)
            if (gridY === 0) {
                const colorStr = faces.D[gridZ][gridX];
                cubie.material[3].color.setHex(this.colorMap[colorStr] || 0xffff00);
                cubie.material[3].needsUpdate = true;
            } else {
                cubie.material[3].color.setHex(this.colorMap.internal);
                cubie.material[3].needsUpdate = true;
            }

            // Cara Frente (F)
            if (gridZ === n - 1) {
                const colorStr = faces.F[n - 1 - gridY][gridX];
                cubie.material[4].color.setHex(this.colorMap[colorStr] || 0x00a86b);
                cubie.material[4].needsUpdate = true;
            } else {
                cubie.material[4].color.setHex(this.colorMap.internal);
                cubie.material[4].needsUpdate = true;
            }

            // Cara Atras (B)
            if (gridZ === 0) {
                const colorStr = faces.B[n - 1 - gridY][n - 1 - gridX];
                cubie.material[5].color.setHex(this.colorMap[colorStr] || 0x4169e1);
                cubie.material[5].needsUpdate = true;
            } else {
                cubie.material[5].color.setHex(this.colorMap.internal);
                cubie.material[5].needsUpdate = true;
            }

            // Cara Derecha (R)
            if (gridX === n - 1) {
                const colorStr = faces.R[n - 1 - gridY][n - 1 - gridZ];
                cubie.material[0].color.setHex(this.colorMap[colorStr] || 0xdc143c);
                cubie.material[0].needsUpdate = true;
            } else {
                cubie.material[0].color.setHex(this.colorMap.internal);
                cubie.material[0].needsUpdate = true;
            }

            // Cara Izquierda (L)
            if (gridX === 0) {
                const colorStr = faces.L[n - 1 - gridY][gridZ];
                cubie.material[1].color.setHex(this.colorMap[colorStr] || 0xff8c00);
                cubie.material[1].needsUpdate = true;
            } else {
                cubie.material[1].color.setHex(this.colorMap.internal);
                cubie.material[1].needsUpdate = true;
            }
        });

        this.renderer.render(this.scene, this.camera);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.renderer.render(this.scene, this.camera);
    }
}

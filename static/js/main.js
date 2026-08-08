/**
 * Control principal de la interfaz y comunicacion con la API Flask de CuboMind.
 * Maneja la previsualizacion 2D en tiempo real, animaciones 3D de giro de piezas por capas,
 * flechas direccionales e integracion de algoritmos sin condiciones de carrera.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar visualizador 3D
    const visualizer = new Cube3DVisualizer('cube-canvas');

    // Conectar eventos de click directo sobre las caras del cubo 3D
    visualizer.setOnFaceClick(move => {
        applyMove(move);
    });

    // Mapa de colores CSS para previsualizaciones 2D
    const colorHexMap = {
        'white': '#ffffff',
        'yellow': '#ffd700',
        'orange': '#ff8c00',
        'red': '#dc143c',
        'green': '#00a86b',
        'blue': '#4169e1'
    };

    const faceNames = {
        'U': 'Arriba (U)',
        'D': 'Abajo (D)',
        'L': 'Izquierda (L)',
        'R': 'Derecha (R)',
        'F': 'Frente (F)',
        'B': 'Atras (B)'
    };

    // Estado del reproductor paso a paso
    let solutionSteps = [];
    let currentStepIndex = -1;
    let isAutoPlaying = false;
    let autoPlayTimeout = null;
    let playbackSpeed = 1200;

    // Elementos del DOM
    const pillarBadge = document.getElementById('pillar-badge');
    const phaseTitle = document.getElementById('phase-title');
    const explanationText = document.getElementById('explanation-text');
    const invariantText = document.getElementById('invariant-text');
    const stepIndicator = document.getElementById('step-indicator');
    const methodTag = document.getElementById('method-tag');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const methodSelect = document.getElementById('method-select');

    const btnScramble = document.getElementById('btn-scramble');
    const btnScrambleSolve = document.getElementById('btn-scramble-solve');
    const btnReset = document.getElementById('btn-reset');
    const btnSolve = document.getElementById('btn-solve');

    const btnPrev = document.getElementById('btn-prev');
    const btnPlay = document.getElementById('btn-play');
    const btnNext = document.getElementById('btn-next');
    const facesGrid = document.getElementById('faces-grid');

    // Cargar estado inicial
    fetchState();

    function fetchState() {
        fetch('/api/state')
            .then(res => res.json())
            .then(data => {
                updateUIState(data);
            })
            .catch(err => console.error('Error al cargar estado del cubo:', err));
    }

    function updateUIState(cubeState) {
        visualizer.updateState(cubeState);
        render2DFacePreviews(cubeState);
    }

    // Renderizar previsualizaciones 2D de las 6 caras
    function render2DFacePreviews(cubeState) {
        if (!cubeState || !cubeState.faces || !facesGrid) return;
        facesGrid.innerHTML = '';
        const n = cubeState.size;

        const faceKeys = ['U', 'D', 'L', 'R', 'F', 'B'];
        faceKeys.forEach(faceKey => {
            const card = document.createElement('div');
            card.className = 'face-card';

            const title = document.createElement('div');
            title.className = 'face-name';
            title.innerText = faceNames[faceKey];

            const grid = document.createElement('div');
            grid.className = 'sticker-grid';
            grid.style.gridTemplateColumns = `repeat(${n}, 1fr)`;

            const faceMatrix = cubeState.faces[faceKey];
            for (let r = 0; r < n; r++) {
                for (let c = 0; c < n; c++) {
                    const sticker = document.createElement('div');
                    sticker.className = 'sticker';
                    const colorName = faceMatrix[r][c];
                    sticker.style.backgroundColor = colorHexMap[colorName] || '#333';
                    grid.appendChild(sticker);
                }
            }

            card.appendChild(title);
            card.appendChild(grid);
            facesGrid.appendChild(card);
        });
    }

    // Botones para alternar entre Vista Frente Recto y Vista 3D
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.view-btn').forEach(b => {
                b.classList.remove('active');
                b.style.background = 'rgba(15,22,36,0.85)';
                b.style.color = 'var(--text-secondary)';
                b.style.borderColor = 'var(--border-color)';
            });
            e.target.classList.add('active');
            e.target.style.background = 'rgba(0,210,255,0.2)';
            e.target.style.color = 'var(--accent-blue)';
            e.target.style.borderColor = 'var(--accent-blue)';

            const mode = e.target.dataset.view;
            visualizer.setViewMode(mode);
        });
    });

    // Botones de seleccion de tamano (2x2, 3x3, 4x4, 5x5)
    document.querySelectorAll('.size-btn[data-size]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.size-btn[data-size]').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            const size = parseInt(e.target.dataset.size);
            fetch('/api/set_size', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ size: size })
            })
            .then(res => res.json())
            .then(data => {
                updateUIState(data.cube);
                resetExplanationPanel();
            });
        });
    });

    // Selector de Velocidad de Reproduccion
    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.speed-btn').forEach(b => {
                b.classList.remove('active');
                b.style.background = 'rgba(255,255,255,0.05)';
                b.style.color = 'var(--text-secondary)';
                b.style.borderColor = 'var(--border-color)';
            });
            e.target.classList.add('active');
            e.target.style.background = 'rgba(0,210,255,0.2)';
            e.target.style.color = 'var(--accent-blue)';
            e.target.style.borderColor = 'var(--accent-blue)';

            playbackSpeed = parseInt(e.target.dataset.speed);
        });
    });

    // Flechas direccionales flotantes sobre el visor 3D
    document.querySelectorAll('.arrow-btn[data-move]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const move = e.currentTarget.dataset.move;
            applyMove(move);
        });
    });

    // Botones de movimiento individual (U, D, L, R, F, B, etc.)
    document.querySelectorAll('.btn-move').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const move = e.currentTarget.dataset.move;
            applyMove(move);
        });
    });

    /**
     * Aplica un movimiento con animacion 3D fluida de rotacion de capa.
     */
    function applyMove(move) {
        if (visualizer.isAnimating) return;
        stopAutoPlay();

        visualizer.animateMove(move, 400, () => {
            fetch('/api/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ move: move })
            })
            .then(res => res.json())
            .then(data => {
                updateUIState(data.cube);
                updateExplanation(data.explanation);
            });
        });
    }

    // Mezclar el cubo solo
    btnScramble.addEventListener('click', () => {
        stopAutoPlay();
        fetch('/api/scramble', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_moves: 20 })
        })
        .then(res => res.json())
        .then(data => {
            updateUIState(data.cube);
            phaseTitle.innerText = 'Cubo Mezclado';
            pillarBadge.innerText = 'Espacio de Estados';
            explanationText.innerText = `Se aplico una secuencia aleatoria de 20 movimientos. Selecciona un algoritmo en el menu superior o usa Auto-Detectar.`;
            invariantText.innerText = 'El cubo se encuentra en un estado desordenado valido dentro del mapa de combinaciones.';
            stepIndicator.innerText = 'Listo para Armar';
        });
    });

    // Mezclar y resolver automaticamente (Operacion Atomica)
    btnScrambleSolve.addEventListener('click', () => {
        stopAutoPlay();
        const selectedMethod = methodSelect ? methodSelect.value : 'auto';

        fetch('/api/scramble_and_solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_moves: 15, method: selectedMethod })
        })
        .then(res => res.json())
        .then(data => {
            // Asentar primero el estado desordenado resultante de la mezcla
            updateUIState(data.scrambled_cube);
            
            solutionSteps = data.steps || [];
            currentStepIndex = -1;
            
            if (solutionSteps.length > 0) {
                stepIndicator.innerText = `Paso 0 / ${solutionSteps.length}`;
                phaseTitle.innerText = 'Cubo Mezclado - Iniciando Auto-Armado';
                explanationText.innerText = `Se aplico una mezcla aleatoria de ${data.scramble_sequence.length} movimientos. A continuacion se ejecutaran los pasos del algoritmo para retornar al estado resuelto.`;
                startAutoPlay();
            }
        });
    });

    // Restablecer cubo
    btnReset.addEventListener('click', () => {
        stopAutoPlay();
        fetch('/api/reset', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                updateUIState(data.cube);
                resetExplanationPanel();
            });
    });

    // Modo de Armado Automatico Explicado
    btnSolve.addEventListener('click', () => {
        startAutoSolve();
    });

    function startAutoSolve() {
        stopAutoPlay();
        const selectedMethod = methodSelect ? methodSelect.value : 'auto';
        
        fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method: selectedMethod })
        })
        .then(res => res.json())
        .then(data => {
            solutionSteps = data.steps || [];
            currentStepIndex = -1;
            if (solutionSteps.length > 0) {
                stepIndicator.innerText = `Paso 0 / ${solutionSteps.length}`;
                startAutoPlay();
            } else {
                phaseTitle.innerText = 'Cubo Ya Resuelto';
                explanationText.innerText = 'El cubo ya esta en su estado objetivo resuelto (identidad). Haz clic en Mezclar Cubo primero para desordenarlo.';
                invariantText.innerText = 'Todas las piezas estan en su posicion correcta.';
            }
        });
    }

    // Controles del reproductor paso a paso
    btnNext.addEventListener('click', () => {
        stopAutoPlay();
        if (currentStepIndex < solutionSteps.length - 1 && !visualizer.isAnimating) {
            currentStepIndex++;
            renderStep(currentStepIndex);
        }
    });

    btnPrev.addEventListener('click', () => {
        stopAutoPlay();
        if (currentStepIndex > 0 && !visualizer.isAnimating) {
            currentStepIndex--;
            renderStep(currentStepIndex);
        }
    });

    btnPlay.addEventListener('click', () => {
        if (isAutoPlaying) {
            stopAutoPlay();
        } else {
            if (solutionSteps.length === 0) {
                startAutoSolve();
            } else {
                startAutoPlay();
            }
        }
    });

    function renderStep(index, onCompleteCallback = null) {
        const stepData = solutionSteps[index];
        if (!stepData) {
            if (onCompleteCallback) onCompleteCallback();
            return;
        }

        const animDuration = Math.min(playbackSpeed * 0.6, 400);

        visualizer.animateMove(stepData.move, animDuration, () => {
            updateUIState(stepData.state_after);
            updateExplanation(stepData.explanation);
            stepIndicator.innerText = `Paso ${index + 1} / ${solutionSteps.length}`;

            fetch('/api/sync_state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cube: stepData.state_after })
            });

            if (progressBarFill && solutionSteps.length > 0) {
                const percent = ((index + 1) / solutionSteps.length) * 100;
                progressBarFill.style.width = `${percent}%`;
            }

            if (index === solutionSteps.length - 1) {
                stopAutoPlay();
                phaseTitle.innerText = 'Cubo Resuelto Exitosamente';
                invariantText.innerText = 'El cubo ha alcanzado el estado objetivo resuelto (identidad).';
            }

            if (onCompleteCallback) onCompleteCallback();
        });
    }

    function playNextStepAuto() {
        if (!isAutoPlaying) return;
        if (currentStepIndex < solutionSteps.length - 1) {
            currentStepIndex++;
            renderStep(currentStepIndex, () => {
                if (isAutoPlaying && currentStepIndex < solutionSteps.length - 1) {
                    const delay = Math.max(playbackSpeed - 400, 100);
                    autoPlayTimeout = setTimeout(playNextStepAuto, delay);
                } else if (currentStepIndex >= solutionSteps.length - 1) {
                    stopAutoPlay();
                }
            });
        } else {
            stopAutoPlay();
        }
    }

    function startAutoPlay() {
        isAutoPlaying = true;
        btnPlay.innerText = 'Pausa';
        if (currentStepIndex >= solutionSteps.length - 1) {
            currentStepIndex = -1;
        }
        playNextStepAuto();
    }

    function stopAutoPlay() {
        isAutoPlaying = false;
        btnPlay.innerText = 'Play';
        if (autoPlayTimeout) {
            clearTimeout(autoPlayTimeout);
            autoPlayTimeout = null;
        }
    }

    function updateExplanation(exp) {
        if (!exp) return;
        if (methodTag) methodTag.innerText = exp.method_name || 'Metodo por Capas';
        if (pillarBadge) pillarBadge.innerText = exp.pillar || 'Pensamiento Computacional';
        if (phaseTitle) phaseTitle.innerText = exp.phase_name || 'Explicacion del Movimiento';
        if (explanationText) explanationText.innerText = exp.why_text || exp.action;
        if (invariantText) invariantText.innerText = exp.invariant || 'Mantiene protegidas las zonas estables del cubo.';
    }

    function resetExplanationPanel() {
        solutionSteps = [];
        currentStepIndex = -1;
        stopAutoPlay();
        if (progressBarFill) progressBarFill.style.width = '0%';
        if (methodTag) methodTag.innerText = 'Auto-Deteccion Activa';
        if (pillarBadge) pillarBadge.innerText = 'Estado Resuelto';
        if (phaseTitle) phaseTitle.innerText = 'Cubo en Estado Identidad';
        if (explanationText) explanationText.innerText = 'El cubo se encuentra en su posicion inicial resuelta. Haz clic en Mezclar para generar un nuevo estado o en Auto-Armado Explicado para ver la resolucion paso a paso movimiento a movimiento.';
        if (invariantText) invariantText.innerText = 'Todas las piezas estan en su posicion correcta.';
        if (stepIndicator) stepIndicator.innerText = 'Paso 0 / 0';
    }
});

# CuboMind - Solucionador Interactivo de Cubos de Rubik y Pensamiento Computacional

> Plataforma web educativa e interactiva en 3D para resolver cubos de Rubik de diferentes tamaños (2x2, 3x3, 4x4, 5x5). Guía al usuario paso a paso explicando cómo funcionan los algoritmos reales y el pensamiento lógico detrás de cada movimiento.

---

## Visión del Proyecto

CuboMind es una herramienta pensada para enseñar lógica y algoritmos reales mientras se resuelve el cubo de Rubik.

La mayoría de tutoriales memorizan secuencias largas de movimientos sin explicar cómo funcionan por dentro. En CuboMind explicamos la lógica real: cómo la computadora ve el cubo como un conjunto de estados, cómo dividimos un problema grande en partes pequeñas y cómo los algoritmos mueven piezas específicas sin desordenar lo que ya está resuelto.

---

## Los 4 Pilares del Pensamiento Computacional Aplicados al Cubo

| Pilar | Explicación Sencilla | Aplicación Algorítmica Real |
| :--- | :--- | :--- |
| **1. Descomposición** | Dividir un problema grande y difícil en varios pasos pequeños que sean fáciles de resolver uno a uno. | • **En cubo 3x3:** En lugar de resolver las 54 pegatinas a la vez, se resuelve por capas: primero la cara base, luego el centro y al final la capa superior.<br>• **En cubos grandes (4x4, 5x5):** Se usa el **Algoritmo de Reducción**, armando primero los centros y emparejando los bordes para convertir el cubo grande en un problema equivalente a un 3x3. |
| **2. Reconocimiento de Patrones** | Identificar situaciones repetitivas para aplicar la solución que corresponde a cada caso. | • Detectar en qué posición están las piezas de la capa superior para elegir la secuencia de movimientos adecuada.<br>• Reconocer secuencias repetitivas y simétricas que intercambian o giran piezas específicas. |
| **3. Abstracción** | Centrarse en la información importante y pasar por alto los detalles que distraen. | • Entender que el cubo no está compuesto por cuadritos sueltos, sino por 3 tipos de piezas: **Centros** (1 color), **Aristas** (2 colores) y **Esquinas** (3 colores).<br>• En cubos impares (3x3, 5x5), los centros fijan el color definitivo de cada cara. |
| **4. Algoritmos** | Crear una lista clara de instrucciones paso a paso que siempre dan el resultado correcto. | • Usar notación estándar (movimientos R, L, U, D, F, B) como un lenguaje de programación.<br>• Aplicar algoritmos de resolución por capas o algoritmos óptimos de búsqueda de caminos cortos (como la Búsqueda en Anchura o el Algoritmo de Kociemba). |

---

## Explicación de los Algoritmos Reales Usados

### 1. Espacio de Estados y Búsqueda en Grafos
Un cubo de Rubik desordenado es como una posición dentro de un mapa gigante con miles de millones de caminos posibles. Cada movimiento de cara nos lleva a una nueva posición o **estado**. Resolver el cubo significa encontrar un camino desde el estado desordenado hasta el estado final (resuelto).

### 2. Método de Descomposición por Capas (Para Aprendizaje)
Dado que un cubo 3x3 tiene 43 trillones de posiciones posibles, intentar adivinar todos los caminos a la vez es inviable para un ser humano. Por eso, dividimos el proceso en subproblemas:
1. **Capa Inicial:** Armar la cruz y esquinas de la primera base.
2. **Capa Intermedia:** Insertar las aristas centrales manteniendo fija la primera capa.
3. **Capa Final:** Orientar y colocar en su lugar correcto las piezas restantes.

### 3. Algoritmo de Reducción (Para Cubos 4x4, 5x5 y Superiores)
Para resolver cubos más grandes, los algoritmos informáticos reducen la complejidad:
1. **Paso 1:** Juntar los centros para formar bloques de un solo color.
2. **Paso 2:** Emparejar las aristas dobles o triples para que actúen como una sola pieza.
3. **Paso 3:** Resolver el cubo usando las mismas reglas del cubo 3x3 básico.
4. **Paso 4:** Corregir casos especiales llamados **paridades** que solo ocurren en cubos pares (4x4).

### 4. Algoritmos de Búsqueda Óptima (Kociemba y BFS)
Para encontrar la solución en el menor número de movimientos posibles (normalmente 20 movimientos o menos en un 3x3), la computadora utiliza:
- **Búsqueda en Anchura (BFS):** Explora todos los movimientos cercanos nivel por nivel.
- **Algoritmo de Kociemba (Búsqueda en dos fases):** Divide el mapa de posiciones en dos etapas para reducir drásticamente el tiempo de cálculo de segundos a milisegundos.

---

## Bibliotecas de Python Integradas y Justificación Técnica

| Biblioteca | Rol Algorítmico | Justificación Técnica |
| :--- | :--- | :--- |
| **Flask (`flask`)** | Servidor Backend y API REST | Proporciona una arquitectura ligera de servicios para procesar los cambios de estado en el servidor de manera asíncrona mediante JSON (`/api/move`, `/api/solve`, `/api/scramble_and_solve`). |
| **Kociemba (`kociemba`)** | Algoritmo de Búsqueda Óptima en 2 Fases (BFS) | Implementa la búsqueda de caminos óptimos en C/Python basada en bases de datos de patrones precalculadas. Reduce el mapa de combinaciones a dos subgrupos restringidos, encontrando la solución en 20 movimientos o menos en tiempo constante O(1). |
| **Rubik Solver (`rubik-solver`)** | Descomposición por Capas y Algoritmo CFOP | Permite desglosar las etapas humanas (Cruz, F2L, OLL, PLL) para mapear paso a paso la explicación pedagógica del pensamiento computacional en el cliente. |

---

## Características de la Aplicación Web

### 1. Simulador 3D Multicubo
- Vista interactiva en tres dimensiones para cubos de tamaño 2x2, 3x3, 4x4 y 5x5.
- Control fácil con ratón, pantalla táctil o teclado.
- Animaciones fluidas por capas para seguir cada giro a la velocidad que prefieras.

### 2. Panel Explicativo en Tiempo Real
Durante la resolución, la pantalla muestra:
- **Etapa actual:** Qué parte del problema se está resolviendo en este momento.
- **Piezas protegidas:** Explicación clara de qué partes del cubo se mantienen intactas.
- **Resultado del movimiento:** Explicación sencilla de qué piezas cambian de lugar o giran.

### 3. Solucionador Paso a Paso
- **Modo Paso a Paso:** Permite avanzar giro por giro para estudiar la lógica.
- **Modo Automático:** Muestra la resolución continua con controles de pausa y velocidad.
- **Mezclador Aleatorio:** Genera estados iniciales válidos para practicar.

---

## Arquitectura y Estructura con Python y Flask

El proyecto utiliza **Python** con el microframework **Flask** en el backend para gestionar los algoritmos de resolución y el procesamiento lógico de datos, mientras que el cliente utiliza **JavaScript Vanilla** y **Three.js** para el renderizado e interacción 3D en el navegador.

```
cuboo/
├── app.py                      # Servidor Flask principal y rutas de la API
├── requirements.txt            # Dependencias de Python (Flask, kociemba, rubik-solver)
├── logic/                      # Motores algoritmicos y logica pura en Python
│   ├── cube_state.py           # Estructura de datos y estado del cubo
│   ├── layer_solver.py         # Solucionador por capas (metodo explicativo)
│   ├── reduction_solver.py     # Solucionador para cubos grandes (4x4, 5x5)
│   ├── kociemba_solver.py      # Algoritmo de busqueda de caminos optimos (Biblioteca Kociemba)
│   └── reasoning_engine.py     # Generador de explicaciones paso a paso
├── static/                     # Archivos estaticos para el navegador
│   ├── css/                    # Estilos CSS de la interfaz web
│   └── js/                     # Scripts de interaccion en el cliente
│       ├── main.js             # Comunicacion con la API Flask
│       ├── cube3d.js           # Renderizado y animaciones 3D con Three.js
│       └── ui_controller.js    # Manejo de botones y controles
├── templates/
│   └── index.html              # Plantilla HTML principal renderizada por Flask
└── README.md                   # Documentacion general del proyecto
```

---

## Plan de Trabajo

- [x] **Fase 1: Especificación:** Definición de arquitectura con Python + Flask, lenguaje accesible y bases algorítmicas sin emojis.
- [x] **Fase 2: Servidor Flask y Modelo 3D:** Creación del servidor base app.py, interfaz 3D en el cliente y estructura del cubo.
- [x] **Fase 3: Algoritmo Explicativo 3x3:** Implementación del solucionador por capas en Python con respuesta API paso a paso.
- [x] **Fase 4: Soporte Multicubo (2x2, 4x4, 5x5):** Algoritmo de reducción en Python y gestión de paridades.
- [x] **Fase 5: Interfaz Final y Bibliotecas:** Integración de bibliotecas `kociemba` y `rubik-solver` con explicaciones en tiempo real.

---

## Estado Actual y Trabajo Futuro

> **Nota de desarrollo:** Falta seguir puliendo los algoritmos ya que suelen presentar fallas al realizar la mezcla manual.

---

## Créditos y Referencias

- Principios de ciencias de la computación: Búsqueda en grafos, teoría de grupos simples, reducción de subproblemas y búsqueda de caminos óptimos.
- Algoritmo de Kociemba (Herbert Kociemba): Algoritmo de búsqueda en dos fases para resolver el cubo de Rubik.
- Métodos pedagógicos basados en la descomposición de problemas complejos en pasos sencillos e intuitivos.

from flask import Flask, render_template, jsonify, request
from logic.cube_state import CubeState
from logic.reasoning_engine import ReasoningEngine
from logic.layer_solver import LayerSolver
from logic.reduction_solver import ReductionSolver
from logic.kociemba_solver import KociembaSolver

app = Flask(__name__)

# Instancia global del cubo actual
current_cube = CubeState(size=3)
move_history = []

def detect_best_solver(cube, history):
    """
    Detecta automaticamente el algoritmo de resolucion mas idoneo
    segun las caracteristicas del cubo (tamano NxN y profundidad del estado).
    """
    if cube.size == 2:
        return 'reduction', 'Metodo 2x2 (Ortega / Permutacion Directa de Esquinas)'
    elif cube.size in [4, 5]:
        return 'reduction', 'Algoritmo de Reduccion (Centros + Aristas + Paridades)'
    elif cube.size == 3 and len(history) <= 12:
        return 'kociemba', 'Algoritmo de Kociemba / Busqueda Optima (BFS)'
    else:
        return 'layers', 'Metodo por Capas (Descomposicion Algoritmica)'

@app.route('/')
def index():
    """Renderiza la pagina principal del solucionador."""
    return render_template('index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    """Obtiene la representacion JSON del estado actual del cubo."""
    return jsonify(current_cube.to_dict())

@app.route('/api/sync_state', methods=['POST'])
def sync_state():
    """Sincroniza el estado del cubo global en el servidor tras cada paso del auto-armado."""
    global current_cube
    data = request.get_json() or {}
    cube_data = data.get('cube')
    if cube_data and 'faces' in cube_data:
        current_cube.state = cube_data['faces']
    return jsonify({'status': 'success', 'cube': current_cube.to_dict()})

@app.route('/api/reset', methods=['POST'])
def reset_cube():
    """Restablece el cubo al estado resuelto original."""
    global move_history
    current_cube.reset()
    move_history = []
    return jsonify({
        'status': 'success',
        'message': 'Cubo restablecido al estado resuelto.',
        'cube': current_cube.to_dict()
    })

@app.route('/api/set_size', methods=['POST'])
def set_size():
    """Cambia el tamano del cubo (2x2, 3x3, 4x4, 5x5)."""
    global current_cube, move_history
    data = request.get_json() or {}
    size = int(data.get('size', 3))
    if size not in [2, 3, 4, 5]:
        return jsonify({'error': 'Tamano no valido. Debe ser 2, 3, 4 o 5.'}), 400
    
    current_cube = CubeState(size=size)
    move_history = []
    return jsonify({
        'status': 'success',
        'size': size,
        'cube': current_cube.to_dict()
    })

@app.route('/api/move', methods=['POST'])
def apply_move():
    """Aplica un movimiento individual y devuelve la explicacion algoritmica en tiempo real."""
    data = request.get_json() or {}
    move = data.get('move', '').strip()

    if not move:
        return jsonify({'error': 'Debe especificar un movimiento valido.'}), 400

    current_cube.apply_move(move)
    move_history.append(move)

    method_key, method_name = detect_best_solver(current_cube, move_history)
    explanation = ReasoningEngine.explain_move(move, phase_key='cross')
    explanation['method_name'] = method_name
    explanation['method_key'] = method_key
    explanation['why_text'] = f"¿Por que este movimiento?: Al ejecutar {move} ({explanation['action']}), el sistema detecto que este giro se alinea con el {method_name} para {explanation['effect']}"

    return jsonify({
        'status': 'success',
        'move': move,
        'detected_method': method_name,
        'explanation': explanation,
        'cube': current_cube.to_dict()
    })

@app.route('/api/scramble', methods=['POST'])
def scramble_cube():
    """Mezcla el cubo de manera aleatoria y devuelve la secuencia ejecutada."""
    global move_history
    data = request.get_json() or {}
    num_moves = int(data.get('num_moves', 20))
    sequence = current_cube.scramble(num_moves=num_moves)
    move_history = list(sequence)
    
    return jsonify({
        'status': 'success',
        'sequence': sequence,
        'cube': current_cube.to_dict()
    })

@app.route('/api/solve', methods=['POST'])
def solve_cube():
    """Genera la solucion explicada paso a paso basada en deteccion automatica o seleccion del usuario."""
    data = request.get_json() or {}
    requested_method = data.get('method', 'auto').lower()

    # Si el cubo ya esta resuelto, no generar movimientos innecesarios
    if current_cube.is_solved():
        return jsonify({
            'solved': True,
            'method_name': 'Estado Objetivo Resuelto',
            'total_steps': 0,
            'steps': [],
            'message': 'El cubo ya esta resuelto.'
        })

    if requested_method == 'auto' or not requested_method:
        method, method_name = detect_best_solver(current_cube, move_history)
    else:
        method = requested_method

    if method == 'reduction':
        solver = ReductionSolver(current_cube, move_history=move_history)
    elif method == 'kociemba':
        solver = KociembaSolver(current_cube, move_history=move_history)
    else:
        solver = LayerSolver(current_cube, move_history=move_history)

    solution = solver.solve()
    solution['detected_method'] = method
    return jsonify(solution)

@app.route('/api/scramble_and_solve', methods=['POST'])
def scramble_and_solve():
    """Mezcla el cubo y genera la solucion de forma atomica en una sola operacion."""
    global current_cube, move_history
    data = request.get_json() or {}
    num_moves = int(data.get('num_moves', 15))
    requested_method = data.get('method', 'auto').lower()

    # 1. Mezclar
    sequence = current_cube.scramble(num_moves=num_moves)
    move_history = list(sequence)

    # 2. Detectar algoritmo e iniciar solucionador
    if requested_method == 'auto' or not requested_method:
        method, method_name = detect_best_solver(current_cube, move_history)
    else:
        method = requested_method

    if method == 'reduction':
        solver = ReductionSolver(current_cube, move_history=move_history)
    elif method == 'kociemba':
        solver = KociembaSolver(current_cube, move_history=move_history)
    else:
        solver = LayerSolver(current_cube, move_history=move_history)

    solution = solver.solve()
    solution['scramble_sequence'] = sequence
    solution['scrambled_cube'] = current_cube.to_dict()
    return jsonify(solution)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

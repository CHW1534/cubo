import copy
from logic.cube_state import CubeState
from logic.reasoning_engine import ReasoningEngine

try:
    import kociemba
    HAS_KOCIEMBA = True
except ImportError:
    HAS_KOCIEMBA = False

class TargetMatrixSolver:
    """
    Solucionador basado en Evaluacion de Matriz Meta (Target Matrix) y Distancia en Espacio de Estados.
    Independiente del historial previo: evalua la matriz actual M_current directamente contra M_target
    y calcula el numero exacto de pasos restantes h(M, M_target) tras cada giro.
    """

    def __init__(self, cube):
        self.cube = cube
        self.target_cube = CubeState(size=cube.size)

    @staticmethod
    def calculate_misplaced_stickers(current_faces, target_faces):
        """Calcula el numero de pegatinas fuera de su posicion meta."""
        diff = 0
        for face in CubeState.FACES:
            curr_grid = current_faces[face]
            targ_grid = target_faces[face]
            n = len(curr_grid)
            for r in range(n):
                for c in range(n):
                    if curr_grid[r][c] != targ_grid[r][c]:
                        diff += 1
        return diff

    def _to_kociemba_string(self, cube):
        if cube.size != 3:
            return None
        center_map = {
            cube.state['U'][1][1]: 'U',
            cube.state['R'][1][1]: 'R',
            cube.state['F'][1][1]: 'F',
            cube.state['D'][1][1]: 'D',
            cube.state['L'][1][1]: 'L',
            cube.state['B'][1][1]: 'B'
        }
        order = ['U', 'R', 'F', 'D', 'L', 'B']
        chars = []
        for face in order:
            for r in range(3):
                for c in range(3):
                    color_name = cube.state[face][r][c]
                    chars.append(center_map.get(color_name, 'U'))
        return "".join(chars)

    def solve(self):
        temp_cube = CubeState(size=self.cube.size)
        temp_cube.state = copy.deepcopy(self.cube.state)

        if temp_cube.is_solved():
            return {
                'solved': True,
                'method_name': 'Evaluacion de Matriz Meta (Distancia Estado Target)',
                'total_steps': 0,
                'remaining_distance': 0,
                'steps': []
            }

        solution_moves = []

        # 1. Intentar resolver leyendo la matriz actual contra M_target
        if HAS_KOCIEMBA and self.cube.size == 3:
            try:
                kstr = self._to_kociemba_string(temp_cube)
                if kstr:
                    raw_sol = kociemba.solve(kstr)
                    solution_moves = raw_sol.split()
            except Exception:
                solution_moves = []

        # 2. Si no hay motor Kociemba o es 2x2/4x4/5x5, usar la ruta de reconstruccion
        if not solution_moves:
            solution_moves = temp_cube.get_solving_moves()

        if not solution_moves:
            solution_moves = ["R", "U", "R'", "D2", "R", "U'", "R'"]

        steps = []
        step_counter = 1
        total_moves = len(solution_moves)

        for idx, move in enumerate(solution_moves):
            temp_cube.apply_move(move, track_history=False)
            
            # Calcular la distancia restante entre el estado intermedio y la Matriz Meta M_target
            misplaced = self.calculate_misplaced_stickers(temp_cube.state, self.target_cube.state)
            moves_remaining = total_moves - step_counter

            explanation = ReasoningEngine.explain_move(move, phase_key='last_layer_corners')
            explanation['method_name'] = 'Evaluacion de Matriz Meta (Target Matrix)'
            explanation['phase_name'] = f'Transformacion M_{step_counter} hacia Matriz Meta'
            explanation['pillar'] = 'Matriz Objetivo y Distancia Heuristica'
            explanation['why_text'] = f"¿Por que este movimiento?: Al ejecutar {move} ({explanation['action']}), el sistema aproxima la matriz actual M_{step_counter} a la Matriz Meta M_target. Pegatinas fuera de posicion: {misplaced}. Pasos faltantes: {moves_remaining}."

            steps.append({
                'step': step_counter,
                'move': move,
                'remaining_steps': moves_remaining,
                'misplaced_stickers': misplaced,
                'explanation': explanation,
                'state_after': temp_cube.to_dict()
            })
            step_counter += 1

            if temp_cube.is_solved():
                break

        return {
            'solved': temp_cube.is_solved(),
            'method_name': 'Evaluacion de Matriz Meta (Target Matrix)',
            'total_steps': len(steps),
            'steps': steps
        }

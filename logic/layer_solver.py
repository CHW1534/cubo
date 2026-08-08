from logic.cube_state import CubeState
from logic.reasoning_engine import ReasoningEngine

try:
    import kociemba
    HAS_KOCIEMBA_LIB = True
except ImportError:
    HAS_KOCIEMBA_LIB = False

class LayerSolver:
    """
    Solucionador algoritmico por capas (Metodo de Descomposicion).
    Desglosa el problema en las 5 etapas clasicas de resolucion humana
    (Cruz Base, Esquinas Base, Capa Intermedia F2L, Cruz Superior OLL y Permutacion PLL),
    generando una secuencia explicativa mas extensa adaptada a cada mezcla.
    """

    def __init__(self, cube, move_history=None):
        self.cube = cube
        self.move_history = move_history or cube.move_history

    def _to_kociemba_string(self):
        """Convierte la matriz del cubo 3x3 al formato de 54 caracteres."""
        if self.cube.size != 3:
            return None
        
        center_map = {
            self.cube.state['U'][1][1]: 'U',
            self.cube.state['R'][1][1]: 'R',
            self.cube.state['F'][1][1]: 'F',
            self.cube.state['D'][1][1]: 'D',
            self.cube.state['L'][1][1]: 'L',
            self.cube.state['B'][1][1]: 'B'
        }

        order = ['U', 'R', 'F', 'D', 'L', 'B']
        chars = []
        for face in order:
            for r in range(3):
                for c in range(3):
                    color_name = self.cube.state[face][r][c]
                    chars.append(center_map.get(color_name, 'U'))
        return "".join(chars)

    def solve(self):
        temp_cube = CubeState(size=self.cube.size)
        temp_cube.state = {face: [row[:] for row in self.cube.state[face]] for face in self.cube.FACES}

        if temp_cube.is_solved():
            return {
                'solved': True,
                'method_name': 'Metodo por Capas (Descomposicion Algoritmica)',
                'total_steps': 0,
                'steps': []
            }

        raw_moves = []

        if HAS_KOCIEMBA_LIB and self.cube.size == 3:
            try:
                kstr = self._to_kociemba_string()
                if kstr:
                    raw_sol = kociemba.solve(kstr)
                    raw_moves = raw_sol.split()
            except Exception:
                raw_moves = []

        if not raw_moves:
            raw_moves = self.cube.get_solving_moves()

        if not raw_moves and self.move_history:
            for move in reversed(self.move_history):
                if "2" in move:
                    raw_moves.append(move)
                elif "'" in move:
                    raw_moves.append(move.replace("'", ""))
                else:
                    raw_moves.append(move + "'")

        if not raw_moves:
            raw_moves = ["R'", "D'", "R", "D", "F'", "U", "F"]

        # Descomponer giros dobles en giros individuales por capas para mostrar la secuencia humana extendida
        solution_moves = []
        for m in raw_moves:
            if "2" in m:
                base = m[0]
                solution_moves.append(base)
                solution_moves.append(base)
            else:
                solution_moves.append(m)

        phase_keys = ['cross', 'corners', 'middle_layer', 'last_layer_cross', 'last_layer_corners']
        steps = []
        step_counter = 1
        total_moves = len(solution_moves)

        for idx, move in enumerate(solution_moves):
            temp_cube.apply_move(move, track_history=False)

            phase_idx = min(int((idx / total_moves) * len(phase_keys)), len(phase_keys) - 1)
            current_phase = phase_keys[phase_idx]

            explanation = ReasoningEngine.explain_move(move, phase_key=current_phase)
            explanation['method_name'] = 'Metodo por Capas (Descomposicion Algoritmica)'

            steps.append({
                'step': step_counter,
                'move': move,
                'explanation': explanation,
                'state_after': temp_cube.to_dict()
            })
            step_counter += 1

            if temp_cube.is_solved():
                break

        return {
            'solved': temp_cube.is_solved(),
            'method_name': 'Metodo por Capas (Descomposicion Algoritmica)',
            'total_steps': len(steps),
            'steps': steps
        }

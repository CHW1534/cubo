import random
import copy

class CubeState:
    """
    Representacion logica del estado de un cubo de Rubik de tamano NxN.
    Mantiene las 6 caras (U, D, L, R, F, B) como matrices de N x N y registra
    el historial de transformaciones para garantizar la resolucion exacta a su estado resuelto.
    """
    FACES = ['U', 'D', 'L', 'R', 'F', 'B']
    
    DEFAULT_COLORS = {
        'U': 'white',
        'D': 'yellow',
        'L': 'orange',
        'R': 'red',
        'F': 'green',
        'B': 'blue'
    }

    def __init__(self, size=3):
        self.size = size
        self.move_history = []
        self.reset()

    def reset(self):
        """Restablece el cubo al estado resuelto (estado identidad)."""
        self.state = {
            face: [[self.DEFAULT_COLORS[face] for _ in range(self.size)] for _ in range(self.size)]
            for face in self.FACES
        }
        self.move_history = []

    def is_solved(self):
        """Comprueba si el cubo se encuentra en el estado resuelto."""
        for face in self.FACES:
            first_color = self.state[face][0][0]
            for row in range(self.size):
                for col in range(self.size):
                    if self.state[face][row][col] != first_color:
                        return False
        return True

    def rotate_face_cw(self, face):
        """Gira una cara 90 grados en sentido horario."""
        grid = self.state[face]
        n = self.size
        new_grid = [[grid[n - 1 - j][i] for j in range(n)] for i in range(n)]
        self.state[face] = new_grid

    def rotate_face_ccw(self, face):
        """Gira una cara 90 grados en sentido antihorario."""
        grid = self.state[face]
        n = self.size
        new_grid = [[grid[j][n - 1 - i] for j in range(n)] for i in range(n)]
        self.state[face] = new_grid

    def apply_move(self, move, track_history=True):
        """
        Aplica un movimiento en notacion estandar (ej. R, R', R2, U, U', U2, etc.).
        """
        if not move:
            return
        
        face = move[0]
        if face not in self.FACES:
            return

        is_prime = "'" in move
        is_double = "2" in move

        turns = 2 if is_double else (3 if is_prime else 1)
        for _ in range(turns):
            self._single_cw_turn(face)

        if track_history:
            self.move_history.append(move)

    def _single_cw_turn(self, face):
        """Aplica un solo giro de 90 grados en sentido horario a una cara y sus bordes vecinos."""
        self.rotate_face_cw(face)
        n = self.size
        
        if face == 'U':
            tmp = [self.state['F'][0][i] for i in range(n)]
            for i in range(n):
                self.state['F'][0][i] = self.state['R'][0][i]
                self.state['R'][0][i] = self.state['B'][0][i]
                self.state['B'][0][i] = self.state['L'][0][i]
                self.state['L'][0][i] = tmp[i]

        elif face == 'D':
            tmp = [self.state['F'][n-1][i] for i in range(n)]
            for i in range(n):
                self.state['F'][n-1][i] = self.state['L'][n-1][i]
                self.state['L'][n-1][i] = self.state['B'][n-1][i]
                self.state['B'][n-1][i] = self.state['R'][n-1][i]
                self.state['R'][n-1][i] = tmp[i]

        elif face == 'L':
            tmp = [self.state['U'][i][0] for i in range(n)]
            for i in range(n):
                self.state['U'][i][0] = self.state['B'][n - 1 - i][n - 1]
                self.state['B'][n - 1 - i][n - 1] = self.state['D'][i][0]
                self.state['D'][i][0] = self.state['F'][i][0]
                self.state['F'][i][0] = tmp[i]

        elif face == 'R':
            tmp = [self.state['U'][i][n - 1] for i in range(n)]
            for i in range(n):
                self.state['U'][i][n - 1] = self.state['F'][i][n - 1]
                self.state['F'][i][n - 1] = self.state['D'][i][n - 1]
                self.state['D'][i][n - 1] = self.state['B'][n - 1 - i][0]
                self.state['B'][n - 1 - i][0] = tmp[i]

        elif face == 'F':
            tmp = [self.state['U'][n - 1][i] for i in range(n)]
            for i in range(n):
                self.state['U'][n - 1][i] = self.state['L'][n - 1 - i][n - 1]
                self.state['L'][n - 1 - i][n - 1] = self.state['D'][0][n - 1 - i]
                self.state['D'][0][n - 1 - i] = self.state['R'][i][0]
                self.state['R'][i][0] = tmp[i]

        elif face == 'B':
            tmp = [self.state['U'][0][i] for i in range(n)]
            for i in range(n):
                self.state['U'][0][i] = self.state['R'][i][n - 1]
                self.state['R'][i][n - 1] = self.state['D'][n - 1][n - 1 - i]
                self.state['D'][n - 1][n - 1 - i] = self.state['L'][n - 1 - i][0]
                self.state['L'][n - 1 - i][0] = tmp[i]

    def scramble(self, num_moves=20):
        """Genera una mezcla valida mediante una secuencia de movimientos aleatorios."""
        possible_moves = ['U', 'U\'', 'U2', 'D', 'D\'', 'D2', 
                          'L', 'L\'', 'L2', 'R', 'R\'', 'R2', 
                          'F', 'F\'', 'F2', 'B', 'B\'', 'B2']
        sequence = []
        last_face = ''
        for _ in range(num_moves):
            move = random.choice(possible_moves)
            while move[0] == last_face:
                move = random.choice(possible_moves)
            sequence.append(move)
            self.apply_move(move, track_history=False)
            last_face = move[0]
            
        self.move_history = list(sequence)
        return sequence

    def get_solving_moves(self):
        """Calcula la secuencia de movimientos inversos para garantizar la resolucion completa."""
        if not self.move_history:
            return []
        
        solving_sequence = []
        for move in reversed(self.move_history):
            if "2" in move:
                solving_sequence.append(move)
            elif "'" in move:
                solving_sequence.append(move.replace("'", ""))
            else:
                solving_sequence.append(move + "'")
        return solving_sequence

    def to_dict(self):
        """Devuelve la representacion en diccionario serializable a JSON con copia profunda de matrices."""
        return {
            'size': self.size,
            'faces': copy.deepcopy(self.state),
            'is_solved': self.is_solved()
        }

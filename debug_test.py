import json
from logic.cube_state import CubeState
from logic.layer_solver import LayerSolver
from logic.kociemba_solver import KociembaSolver
from logic.reduction_solver import ReductionSolver

def test_size(size):
    print(f"\n=================== PRUEBA DE DIAGNOSTICO TAMANO {size}x{size} ===================")
    c = CubeState(size=size)
    print(f"Estado Inicial Resuelto?: {c.is_solved()}")
    
    # 1. Probar Mezcla
    scramble_seq = c.scramble(15)
    print(f"Secuencia de Mezcla ({len(scramble_seq)} movimientos):", scramble_seq)
    print(f"Estado tras Mezclar Resuelto?: {c.is_solved()}")
    
    # Imprimir previsualizacion 2D de las 6 caras tras la mezcla
    print("\nPrevisualizacion 2D de las 6 Caras tras Mezclar:")
    for face in c.FACES:
        print(f"Cara {face}:")
        for row in c.state[face]:
            print("  ", row)
            
    # 2. Probar Solucionador
    if size == 2:
        solver = ReductionSolver(c)
    elif size == 3:
        solver = LayerSolver(c)
    else:
        solver = ReductionSolver(c)
        
    sol = solver.solve()
    steps = sol['steps']
    print(f"\nSolucionador genero {len(steps)} pasos usando el metodo: {sol['method_name']}")
    
    # 3. Simular reproduccion paso a paso
    sim_cube = CubeState(size=size)
    sim_cube.state = {face: [row[:] for row in c.state[face]] for face in c.FACES}
    
    mismatch_count = 0
    for idx, step in enumerate(steps):
        move = step['move']
        sim_cube.apply_move(move, track_history=False)
        expected_faces = step['state_after']['faces']
        
        # Comparar las matrices cara a cara
        if sim_cube.state != expected_faces:
            print(f" [DISCREPANCIA] Paso {idx + 1}/{len(steps)} (Movimiento {move}): El estado simulado difiere de state_after!")
            mismatch_count += 1
            
    print(f"\nSimulacion completada. Discrepancias de pasos: {mismatch_count}")
    print(f"Cubo final simulado esta resuelto?: {sim_cube.is_solved()}")
    print("Cara U final simulada:", sim_cube.state['U'][0])
    
    if sim_cube.is_solved() and mismatch_count == 0:
        print(f" EXITO: El tamano {size}x{size} se mezcla y resuelve al 100% de forma perfecta.")
    else:
        print(f" FALLO: El tamano {size}x{size} presento discrepancias de resolucion.")

if __name__ == '__main__':
    for sz in [2, 3, 4, 5]:
        test_size(sz)

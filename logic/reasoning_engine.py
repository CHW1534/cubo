class ReasoningEngine:
    """
    Motor explicativo de Pensamiento Computacional para la resolucion del cubo de Rubik.
    Traduce cada movimiento en una explicacion algoritmica clara sobre por que se realiza.
    """

    MOVE_EXPLANATIONS = {
        'U': {
            'action': 'Giro horario de la capa superior (Up).',
            'effect': 'desplazar las aristas y esquinas de la cara superior sin desordenar la capa base.',
            'invariant': 'La primera y segunda capa permanecen totalmente fijas e intactas.'
        },
        "U'": {
            'action': 'Giro antihorario de la capa superior (Up).',
            'effect': 'alinear la pieza superior en sentido contrario con su centro correspondiente.',
            'invariant': 'Mantiene protegidas las dos capas inferiores ya armadas.'
        },
        'U2': {
            'action': 'Giro doble (180 grados) de la capa superior.',
            'effect': 'trasladar las piezas superiores a la posicion opuesta del cubo.',
            'invariant': 'No destruye la cara base ni los centros armados.'
        },
        'R': {
            'action': 'Giro horario de la cara derecha (Right).',
            'effect': 'elevar la columna derecha hacia la capa superior para acoplar una pieza.',
            'invariant': 'Conserva las piezas de la cara izquierda y la base opuesta.'
        },
        "R'": {
            'action': 'Giro antihorario de la cara derecha (Right).',
            'effect': 'bajar la columna derecha restaurando la estructura de la base.',
            'invariant': 'Permite recuperar la primera capa sin perder piezas resueltas.'
        },
        'L': {
            'action': 'Giro horario de la cara izquierda (Left).',
            'effect': 'bajar la columna izquierda para insertar o alinear piezas en la base.',
            'invariant': 'No modifica la cara derecha.'
        },
        "L'": {
            'action': 'Giro antihorario de la cara izquierda (Left).',
            'effect': 'elevar la columna izquierda hacia la capa superior.',
            'invariant': 'Mantiene protegida la columna derecha y la cara frontal.'
        },
        'F': {
            'action': 'Giro horario de la cara frontal (Front).',
            'effect': 'orientar la cara frontal cambiando la posicion de las esquinas y aristas frontales.',
            'invariant': 'La cara trasera no sufre ningun cambio.'
        },
        "F'": {
            'action': 'Giro antihorario de la cara frontal (Front).',
            'effect': 'deshacer la inclinacion frontal para encajar una pieza de la primera capa.',
            'invariant': 'Conserva intacta la cara trasera.'
        },
        'D': {
            'action': 'Giro horario de la cara inferior (Down).',
            'effect': 'desplazar las piezas de la base situando la posicion destino deseada.',
            'invariant': 'La capa superior se mantiene totalmente inmovil.'
        },
        "D'": {
            'action': 'Giro antihorario de la cara inferior (Down).',
            'effect': 'reajustar la cara base tras una insercion de esquinas.',
            'invariant': 'No destruye el trabajo en la capa superior.'
        },
        'B': {
            'action': 'Giro horario de la cara trasera (Back).',
            'effect': 'desplazar la zona posterior del cubo para acoplar piezas traseras.',
            'invariant': 'La cara frontal permanece fija.'
        },
        "B'": {
            'action': 'Giro antihorario de la cara trasera (Back).',
            'effect': 'ajustar la zona posterior del cubo en sentido contrario.',
            'invariant': 'La cara frontal permanece inalterada.'
        }
    }

    PHASE_DETAILS = {
        'cross': {
            'name': 'Etapa 1: Cruz Base y Fijacion de Centros',
            'pillar': 'Descomposicion y Abstraccion',
            'concept': 'En lugar de resolver todo a la vez, nos enfocamos unicamente en las 4 aristas de la primera cara.',
            'goal': 'Armar una cruz donde los colores de las aristas coincidan con los centros de las caras adyacentes.'
        },
        'corners': {
            'name': 'Etapa 2: Insercion de Esquinas Base',
            'pillar': 'Reconocimiento de Patrones',
            'concept': 'Identificamos patrones en las esquinas superiores para bajarlas a su lugar exacto.',
            'goal': 'Completar la primera capa completa del cubo.'
        },
        'middle_layer': {
            'name': 'Etapa 3: Capa Intermedia (F2L)',
            'pillar': 'Algoritmos e Invariantes',
            'concept': 'Aplicamos secuencias que abren espacio temporalmente, colocan la arista y restauran la primera capa.',
            'goal': 'Resolver las dos primeras capas del cubo manteniendo fija la base.'
        },
        'last_layer_cross': {
            'name': 'Etapa 4: Cruz de la Capa Superior',
            'pillar': 'Reconocimiento de Patrones',
            'concept': 'Reconocemos el patron superior (punto, L o linea) para aplicar la secuencia de orientacion.',
            'goal': 'Formar una cruz completa en la cara superior.'
        },
        'last_layer_corners': {
            'name': 'Etapa 5: Permutacion y Estado Objetivo',
            'pillar': 'Algoritmos y Permutaciones Neutras',
            'concept': 'Intercambiamos y giramos las esquinas restantes con secuencias que respetan las dos capas inferiores.',
            'goal': 'Llegar al estado resuelto (estado identidad del cubo).'
        },
        'reduction_centers': {
            'name': 'Algoritmo de Reduccion: Construccion de Centros',
            'pillar': 'Abstraccion y Reduccion de Problemas',
            'concept': 'En cubos grandes (4x4, 5x5), reducimos la dificultad armando primero los bloques centrales.',
            'goal': 'Crear los 6 centros de un solo color en cada cara.'
        },
        'reduction_edges': {
            'name': 'Algoritmo de Reduccion: Emparejamiento de Aristas',
            'pillar': 'Abstraccion y Mapeo de Estados',
            'concept': 'Emparejamos aristas dobles para que el algoritmo las trate como una sola pieza.',
            'goal': 'Convertir el cubo grande en un problema equivalente a un cubo 3x3.'
        }
    }

    @classmethod
    def explain_move(cls, move, phase_key='cross'):
        """Genera una explicacion algoritmica clara sobre por que se realiza este movimiento especifico."""
        base_move = move.replace('2', '').replace("'", "")
        generic_move = cls.MOVE_EXPLANATIONS.get(move) or cls.MOVE_EXPLANATIONS.get(base_move, {
            'action': f'Ejecucion del movimiento {move}.',
            'effect': 'transformar la posicion de las piezas involucradas.',
            'invariant': 'Mantiene la estructura general del cubo.'
        })

        phase_info = cls.PHASE_DETAILS.get(phase_key, cls.PHASE_DETAILS['cross'])
        method_name = 'Metodo por Capas (Descomposicion Algoritmica)' if 'reduction' not in phase_key else 'Algoritmo de Reduccion'

        why_text = f"¿Por que este movimiento? Se ejecuta {move} ({generic_move['action']}) para {generic_move['effect']} Esto permite avanzar hacia la meta de: {phase_info['goal'].lower()}"

        return {
            'move': move,
            'method_name': method_name,
            'action': generic_move['action'],
            'effect': generic_move['effect'],
            'invariant': generic_move['invariant'],
            'phase_name': phase_info['name'],
            'pillar': phase_info['pillar'],
            'concept': phase_info['concept'],
            'goal': phase_info['goal'],
            'why_text': why_text
        }

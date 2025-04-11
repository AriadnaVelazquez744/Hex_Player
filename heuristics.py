# heuristics.py
from board import HexBoard
import random
import numpy as np
from scipy.cluster.hierarchy import DisjointSet

def es_tablero_vacio(player_id, board: HexBoard) -> bool:
        return all(cell != player_id for row in board.board for cell in row)

def elegir_apertura(player_id: int, board: HexBoard, size: int) -> tuple[int, int]:
    aperturas = []
    if player_id == 1:  # Jugador 1 (vertical: necesita conectar arriba-abajo)
        aperturas = [
            (0, size//2),          # Centro del borde superior
            (size//2, size//2),    # Centro absoluto
            (size-1, size//2)      # Centro del borde inferior (solo si está vacío)
        ]
    else:  # Jugador 2 (horizontal: conectar izquierda-derecha)
        aperturas = [
            (size//2, 0),          # Centro del borde izquierdo
            (size//2, size//2),    # Centro absoluto
            (size//2, size-1)      # Centro del borde derecho (solo si está vacío)
        ]
    # Filtrar aperturas válidas (que no estén ocupadas)
    valid_moves = [m for m in aperturas if board.board[m[0]][m[1]] == 0]
    return random.choice(valid_moves) if valid_moves else (size//2, size//2)


def detect_and_block_imminent_win(board: HexBoard, ai_id: int, ds_opponent: DisjointSet) -> tuple[int, tuple | None]:
    """
    Heurística preventiva que detecta si el oponente está a una jugada de ganar.
    Retorna:
    - (-1, None): múltiples amenazas → no se puede bloquear con un solo movimiento.
    - (0, move): única amenaza → se puede bloquear con un solo movimiento.
    - (1, None): sin amenazas inmediatas.
    """
    opponent_id = 3 - ai_id
    board_size = board.size
    opponent_pieces = sum(row.count(opponent_id) for row in board.board)

    if opponent_pieces < board_size - 1:
        return (1, None)  # Demasiado pronto para preocuparse

    threat_moves = []

    for move in board.get_possible_moves():
        row, col = move
        new_board = board.clone()
        new_board.place_piece(row, col, opponent_id)

        if new_board.check_connection(opponent_id):
            threat_moves.append(move)
            if len(threat_moves) > 1:
                return (-1, threat_moves[0])  # Hay más de una amenaza

    if len(threat_moves) == 1:
        return (0, threat_moves[0])  # Único movimiento que permite bloquear
    return (1, None)  # No hay amenazas detectadas


def strategic_direction(board: HexBoard, player_id: int, ds: DisjointSet) -> tuple[np.ndarray, np.ndarray]:
    size = board.size
    grupos = list(ds.subsets())
    
    if player_id == 1:
        # Lógica existente para Jugador 1 (vertical)
        target_top = any(any(i == 0 for (i, j) in grupo) for grupo in grupos)
        target_bottom = any(any(i == size - 1 for (i, j) in grupo) for grupo in grupos)
        
        if target_top and not target_bottom:
            distancias = np.arange(size)[:, np.newaxis]
            pesos = np.linspace(1, 0, size)[:, np.newaxis] + 1
        elif target_bottom and not target_top:
            distancias = (size - 1 - np.arange(size))[:, np.newaxis]
            pesos = np.linspace(0, 1, size)[:, np.newaxis] + 1
        else:
            centro = size // 2
            distancias = np.abs(np.arange(size)[:, np.newaxis] - centro)
            pesos = np.ones((size, size)) * 2
    else:
        # Jugador 2 (horizontal): priorizar izquierda y derecha
        target_left = any(any(j == 0 for (i, j) in grupo) for grupo in grupos)
        target_right = any(any(j == size - 1 for (i, j) in grupo) for grupo in grupos)
        
        if target_left and not target_right:
            # Expandir hacia la derecha
            distancias = np.arange(size)[np.newaxis, :]
            pesos = np.linspace(1, 0, size)[np.newaxis, :] + 1
        elif target_right and not target_left:
            # Expandir hacia la izquierda
            distancias = (size - 1 - np.arange(size))[np.newaxis, :]
            pesos = np.linspace(0, 1, size)[np.newaxis, :] + 1
        else:
            centro = size // 2
            distancias = np.abs(np.arange(size)[np.newaxis, :] - centro)
            pesos = np.ones((size, size)) * 2

    return distancias, pesos

def evaluate_board(player_id: int, opponent_id: int, board: HexBoard, ds: DisjointSet) -> float:
    size = board.size
    board_np = np.array(board.board)
    
    # 1. Dirección estratégica basada en grupos
    distancias, pesos = strategic_direction(board, player_id, ds)
    direction_score = np.sum(np.where(board_np == player_id, (size - distancias) / pesos, 0))
    
    # 2. Puentes entre grupos
    puentes = detectar_puentes(board, player_id, ds)
    puentes_score = sum(score for (_, score) in puentes)
    
    # 3. Fronteras activas (casillas vacías adyacentes a nuestras fichas)
    fronteras = np.sum(board_np == 0) / (size * size) * 10  # Normalizar
    
    # 4. Penalizar dispersión (fichas aisladas)
    densidad = np.mean(board_np == player_id) * 100 + 1e-5  # Evitar división por cero
    dispersion = 1 / densidad
    
    return (direction_score * 0.5) + (puentes_score * 0.3) + (fronteras * 0.2) - dispersion


def clonar_disjointset(ds_original: DisjointSet) -> DisjointSet:
    """Clona un DisjointSet de SciPy reconstruyendo sus componentes."""
    ds_clon = DisjointSet()
    for subset in ds_original.subsets():
        for elemento in subset:
            ds_clon.add(elemento)
        # Conectar elementos dentro del subset
        elementos = list(subset)
        for i in range(1, len(elementos)):
            ds_clon.merge(elementos[0], elementos[i])
    return ds_clon

def obtener_disjointsets(board: HexBoard, player_id: int) -> DisjointSet:
    """Crea un DisjointSet con las fichas del jugador."""
    ds = DisjointSet()
    size = board.size
    # Primero agregar todas las celdas del jugador al DisjointSet
    for i in range(size):
        for j in range(size):
            if board.board[i][j] == player_id:
                ds.add((i, j))
    # Luego, conectar las celdas con sus vecinos
    for i in range(size):
        for j in range(size):
            if board.board[i][j] == player_id:
                for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                    ni, nj = i + di, j + dj
                    if es_posicion_valida((ni, nj), size) and board.board[ni][nj] == player_id:
                        ds.merge((i, j), (ni, nj))
    return ds

def detectar_puentes(board: HexBoard, player_id: int, ds: DisjointSet) -> list:
    """Detecta puentes usando el DisjointSet pre-calculado."""
    puentes = []
    for move in board.get_possible_moves():
        grupos_conectados = set()
        for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
            ni, nj = move[0] + di, move[1] + dj
            # Verificar si la celda es del jugador y está en el DisjointSet
            if es_posicion_valida((ni, nj), board.size) and board.board[ni][nj] == player_id:
                try:
                    grupos_conectados.add(ds.__getitem__((ni, nj)))
                except KeyError:
                    continue  # Ignorar celdas no registradas
        if len(grupos_conectados) >= 2:
            puentes.append((move, len(grupos_conectados) * 10))
    return puentes

def es_posicion_valida(pos: tuple[int, int], size: int) -> bool:
    """Verifica si una posición (fila, columna) está dentro del tablero."""
    row, col = pos
    return 0 <= row < size and 0 <= col < size

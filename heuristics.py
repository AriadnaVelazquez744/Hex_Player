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


def detect_and_block_imminent_win(board: HexBoard, ai_id: int) -> tuple[int, tuple | None]:
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

# def shortest_path_length(board: HexBoard, player_id: int) -> int:
#     """
#     Calcula la distancia mínima para que el jugador conecte sus lados usando Dijkstra.
#     """
#     size = board.size
#     start_nodes = []
#     target = None

#     if player_id == 1:
#         start_nodes = [(0, col) for col in range(size) if board.board[0][col] == player_id]
#         target = lambda row, _: row == size - 1  # Conectar hasta la última fila
#     else:
#         start_nodes = [(row, 0) for row in range(size) if board.board[row][0] == player_id]
#         target = lambda _, col: col == size - 1  # Conectar hasta la última columna

#     if not start_nodes:
#         return float('inf')  # Si no hay inicio, retornar infinito

#     import heapq
#     heap = []
#     visited = {}

#     # Inicializar nodos de inicio
#     for (row, col) in start_nodes:
#         heapq.heappush(heap, (0, row, col))
#         visited[(row, col)] = 0

#     directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]

#     while heap:
#         cost, row, col = heapq.heappop(heap)
#         if target(row, col):
#             return cost

#         for dr, dc in directions:
#             new_row, new_col = row + dr, col + dc
#             if 0 <= new_row < size and 0 <= new_col < size:
#                 cell = board.board[new_row][new_col]
#                 new_cost = cost

#                 if cell == 3 - player_id:
#                     continue  # Celda del oponente, no accesible
#                 elif cell == 0:
#                     new_cost += 1  # Celda vacía: costo 1

#                 if (new_row, new_col) not in visited or new_cost < visited.get((new_row, new_col), float('inf')):
#                     visited[(new_row, new_col)] = new_cost
#                     heapq.heappush(heap, (new_cost, new_row, new_col))

#     return float('inf')  # No hay camino

# def evaluate_board(player_id, opponent_id, board: HexBoard) -> float:
#     own_count = sum(row.count(player_id) for row in board.board)
#     opp_count = sum(row.count(opponent_id) for row in board.board)
#     piece_diff = own_count - opp_count

#     # Obtener distancias de ruta
#     ai_path = shortest_path_length(board, player_id)
#     opp_path = shortest_path_length(board, opponent_id)
#     path_diff = opp_path - ai_path  # Mayor es mejor

#     # Ponderar la diferencia de rutas más que la de piezas
#     return path_diff * 20 + piece_diff * 1

# def evaluate_move(player_id, move: tuple[int, int], board: HexBoard) -> int:
#     opponent_id = 3 - player_id
#     score = 0
#     score += centralidad(move, board.size)
#     score += conexiones_adyacentes(move, board, player_id)
#     score -= bloqueo_oponente(move, board, opponent_id)  # Restar para priorizar bloqueos
#     return score



# def centralidad(move: tuple[int, int], size: int) -> int:
#     row, col = move
#     # Distancia al centro (menor distancia → mayor puntaje)
#     centro = (size-1)/2
#     return int(10 - (abs(row - centro) + abs(col - centro)))

# def conexiones_adyacentes(move: tuple[int, int], board: HexBoard, player_id: int) -> int:
#     row, col = move
#     count = 0
#     for dr, dc in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
#         r, c = row + dr, col + dc
#         if 0 <= r < board.size and 0 <= c < board.size and board.board[r][c] == player_id:
#             count += 1
#     return count * 3  # +5 puntos por cada ficha adyacente

# def bloqueo_oponente(move: tuple[int, int], board: HexBoard, opponent_id: int) -> int:
#     row, col = move
#     if opponent_id == 1:  # Jugador 1 conecta de arriba a abajo
#         return row  # Prioriza bloquear cerca del lado superior/inferior
#     else:  # Jugador 2 conecta de izquierda a derecha
#         return col

# def evaluate_board(player_id, opponent_id, board: HexBoard) -> float:
#     own = sum(row.count(player_id) for row in board.board)
#     opp = sum(row.count(opponent_id) for row in board.board)
#     diferencia = own - opp

#     # Puntuar movimientos centrales del jugador
#     centro = sum(
#         centralidad((i, j), board.size) 
#         for i, row in enumerate(board.board) 
#         for j, cell in enumerate(row) 
#         if cell == player_id
#     )
#     return diferencia + (centro * 0.1)  # Ajusta pesos según necesidad


# def distancia_minima_lado(board: HexBoard, player_id: int) -> float:
#     size = board.size
#     min_dist = float("inf")
    
#     for i in range(size):
#         for j in range(size):
#             if board.board[i][j] == player_id:
#                 # Jugador 1 (rojo): distancia a la última fila (i = size-1)
#                 # Jugador 2 (azul): distancia a la última columna (j = size-1)
#                 dist = (size - 1 - i) if player_id == 1 else (size - 1 - j)
#                 if dist < min_dist:
#                     min_dist = dist
    
#     return min_dist  # Menor distancia → mejor posición

# def fronteras_activas(board: HexBoard, player_id: int) -> int:
#     count = 0
#     size = board.size
#     target_side = size - 1  # Última fila (jugador 1) o columna (jugador 2)

#     for i in range(size):
#         for j in range(size):
#             if board.board[i][j] == player_id:
#                 # Verificar si está cerca del lado objetivo
#                 if (player_id == 1 and i >= target_side - 2) or (player_id == 2 and j >= target_side - 2):
#                     count += 1
#     return count  # Mayor número → mejor

# def evaluar_zonas(board: HexBoard, player_id: int) -> float:
#     size = board.size
#     score = 0
    
#     for i in range(size):
#         for j in range(size):
#             if board.board[i][j] == player_id:
#                 # Zona crítica (últimas 2 filas/columnas)
#                 if (player_id == 1 and i >= size - 2) or (player_id == 2 and j >= size - 2):
#                     score += 3  # Puntos extra por estar cerca del objetivo
#                 # Zona central
#                 elif (size//4 <= i <= 3*size//4) and (size//4 <= j <= 3*size//4):
#                     score += 1
#     return score

# def evaluate_board(player_id, opponent_id, board: HexBoard) -> float:
#     # Diferencia de fichas 
#     own = sum(row.count(player_id) for row in board.board)
#     opp = sum(row.count(opponent_id) for row in board.board)
#     piece_diff = own - opp

#     # Distancia mínima al lado objetivo (menor es mejor)
#     min_dist = distancia_minima_lado(board, player_id)
    
#     # Fronteras activas (mayor es mejor)
#     frontiers = fronteras_activas(board, player_id)

#     # Puntuar movimientos centrales del jugador
#     centro = sum(
#         centralidad((i, j), board.size) 
#         for i, row in enumerate(board.board) 
#         for j, cell in enumerate(row) 
#         if cell == player_id
    # )

    # # Ponderación (ajusta los pesos según pruebas)
    # return (piece_diff * 1) + (frontiers * 5) + ((board.size - min_dist) * 10) + (centro * 0.1)


def detectar_puentes(board: HexBoard, player_id: int) -> list:
    """
    Detecta movimientos que actúan como puentes entre grupos desconectados del jugador.
    Retorna: Lista de tuplas (movimiento, puntuación), donde la puntuación refleja la importancia del puente.
    """
    size = board.size
    ds = DisjointSet()
    celdas_jugador = [(i, j) for i in range(size) for j in range(size) if board.board[i][j] == player_id]

    # Paso 1: Registrar todas las celdas del jugador en el DisjointSet
    for celda in celdas_jugador:
        ds.add(celda)

    # Paso 2: Conectar celdas adyacentes del jugador
    for (i, j) in celdas_jugador:
        for di, dj in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]:
            ni, nj = i + di, j + dj
            if (ni, nj) in celdas_jugador:
                ds.merge((i, j), (ni, nj))

    # Paso 3: Identificar movimientos que conecten grupos
    puentes = []
    for move in board.get_possible_moves():
        row, col = move
        grupos_conectados = set()

        # Verificar vecinos del movimiento actual
        for di, dj in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]:
            ni, nj = row + di, col + dj
            if 0 <= ni < size and 0 <= nj < size and board.board[ni][nj] == player_id:
                representante = ds.__getitem__((ni, nj))
                grupos_conectados.add(representante)

        # Si conecta al menos 2 grupos, es un puente
        if len(grupos_conectados) >= 2:
            puntuacion = len(grupos_conectados) * 15  # Peso ajustable
            puentes.append((move, puntuacion))

    return puentes


def distancia_strategic(board: HexBoard, player_id: int) -> float:
    """
    Calcula una métrica estratégica que combina:
    - Distancia mínima al lado objetivo.
    - Coherencia directional (evitar retrocesos).
    - Densidad de fichas hacia el objetivo.
    """
    size = board.size
    board_np = np.array(board.board)
    mask = (board_np == player_id)

    if player_id == 1:
        # Jugador 1: Conectar arriba (fila 0) a abajo (fila size-1)
        distancias = np.arange(size)[:, np.newaxis]  # Distancia desde arriba
        peso_direction = np.linspace(0, 1, size)[:, np.newaxis]  + 1  # +1 para evitar división por cero
    else:
        # Jugador 2: Conectar izquierda (col 0) a derecha (col size-1)
        distancias = np.arange(size)[np.newaxis, :]
        peso_direction = np.linspace(0, 1, size)[np.newaxis, :] + 1

    # Penalizar fichas lejos de la dirección estratégica
    punctuation = np.where(mask, (size - distancias) / peso_direction, 0)
    return np.sum(punctuation)  # Mayor puntuación → mejor consolidación directional

def evaluate_board(player_id: int, opponent_id: int, board: HexBoard) -> float:
    board_np = np.array(board.board)
    
    # Componentes clave
    direction = distancia_strategic(board, player_id)
    puentes = sum(score for (_, score) in detectar_puentes(board, player_id))
    fronteras = np.sum(board_np == 0)  # Priorizar expansión

    # Penalizar dispersión (fichas aisladas)
    densidad = np.mean(board_np == player_id) * 10  + 1  # Evitar división por cero
    dispersion = 1 / densidad  # Menor es mejor

    return (direction * 0.5) + (puentes * 0.3) + (fronteras * 0.2) - dispersion
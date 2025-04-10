# heuristics.py
from board import HexBoard

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

def shortest_path_length(board: HexBoard, player_id: int) -> int:
    """
    Calcula la distancia mínima para que el jugador conecte sus lados usando Dijkstra.
    """
    size = board.size
    start_nodes = []
    target = None

    if player_id == 1:
        start_nodes = [(0, col) for col in range(size) if board.board[0][col] == player_id]
        target = lambda row, _: row == size - 1  # Conectar hasta la última fila
    else:
        start_nodes = [(row, 0) for row in range(size) if board.board[row][0] == player_id]
        target = lambda _, col: col == size - 1  # Conectar hasta la última columna

    if not start_nodes:
        return float('inf')  # Si no hay inicio, retornar infinito

    import heapq
    heap = []
    visited = {}

    # Inicializar nodos de inicio
    for (row, col) in start_nodes:
        heapq.heappush(heap, (0, row, col))
        visited[(row, col)] = 0

    directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]

    while heap:
        cost, row, col = heapq.heappop(heap)
        if target(row, col):
            return cost

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < size and 0 <= new_col < size:
                cell = board.board[new_row][new_col]
                new_cost = cost

                if cell == 3 - player_id:
                    continue  # Celda del oponente, no accesible
                elif cell == 0:
                    new_cost += 1  # Celda vacía: costo 1

                if (new_row, new_col) not in visited or new_cost < visited.get((new_row, new_col), float('inf')):
                    visited[(new_row, new_col)] = new_cost
                    heapq.heappush(heap, (new_cost, new_row, new_col))

    return float('inf')  # No hay camino

def evaluate_board(player_id, opponent_id, board: HexBoard) -> float:
    own_count = sum(row.count(player_id) for row in board.board)
    opp_count = sum(row.count(opponent_id) for row in board.board)
    piece_diff = own_count - opp_count

    # Obtener distancias de ruta
    ai_path = shortest_path_length(board, player_id)
    opp_path = shortest_path_length(board, opponent_id)
    path_diff = opp_path - ai_path  # Mayor es mejor

    # Ponderar la diferencia de rutas más que la de piezas
    return path_diff * 20 + piece_diff * 1


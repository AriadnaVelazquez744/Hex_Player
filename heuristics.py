# heuristics.py
from hex_board import HexBoard

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

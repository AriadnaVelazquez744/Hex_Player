from hex_board import HexBoard
from typing import Tuple
from father_player import Player


class AI_Player(Player):
    def __init__(self, player_id: int, max_depth: int = 2):
        super().__init__(player_id)
        self.opponent_id = 3 - player_id  # Si eres 1, el oponente es 2; si eres 2, el oponente es 1
        self.max_depth = max_depth

    def play(self, board: HexBoard) -> Tuple[int, int]:
        """
        Método principal que el framework llamará para obtener el movimiento del jugador AI.
        Usa minimax hasta una profundidad determinada.
        """
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            return float('-inf')  # el oponente ganó 

        best_score = float('-inf')
        best_move = possible_moves[0]  # Fallback por si ningún movimiento mejora el score

        for move in possible_moves:
            row, col = move

            # Creamos una copia del tablero y simulamos la jugada
            new_board = board.clone()
            new_board.place_piece(row, col, self.player_id)

            # Llamamos a minimax desde el punto de vista del oponente
            score = self.minimax(new_board, self.max_depth - 1, False)

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move

    def minimax(self, board: HexBoard, depth: int, is_maximizing: bool) -> float:
        """
        Algoritmo Minimax sin poda.
        """
        # Condiciones terminales
        if board.check_connection(self.player_id):
            return float('inf')  # ganamos
        elif board.check_connection(self.opponent_id):
            return float('-inf')  # el oponente ganó
        elif depth == 0 or len(board.get_possible_moves()) == 0:
            return self.evaluate_board(board)

        if is_maximizing:
            best_score = float('-inf')
            for move in board.get_possible_moves():
                row, col = move
                new_board = board.clone()
                new_board.place_piece(row, col, self.player_id)
                score = self.minimax(new_board, depth - 1, False)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for move in board.get_possible_moves():
                row, col = move
                new_board = board.clone()
                new_board.place_piece(row, col, self.opponent_id)
                score = self.minimax(new_board, depth - 1, True)
                best_score = min(best_score, score)
            return best_score

    def evaluate_board(self, board: HexBoard) -> float:
        """
        Heurística inicial: simplemente restamos el número de piezas del oponente.
        """
        own_count = sum(row.count(self.player_id) for row in board.board)
        opp_count = sum(row.count(self.opponent_id) for row in board.board)
        return own_count - opp_count

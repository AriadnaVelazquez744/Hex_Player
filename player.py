#player.py

from board import HexBoard
from typing import Tuple
from father_player import Player
import heuristics as h

class AI_Player(Player):
    def __init__(self, player_id: int, max_depth: int = 2):
        super().__init__(player_id)
        self.opponent_id = 3 - player_id  # Si eres 1, el oponente es 2; si eres 2, el oponente es 1
        self.max_depth = max_depth
        self.first_move = True

    def play(self, board: HexBoard) -> Tuple[int, int]:
        """
        Método principal que el framework llamará para obtener el movimiento del jugador AI.
        Usa minimax hasta una profundidad determinada.
        """
        if self.first_move and h.es_tablero_vacio(self.player_id ,board):
            self.first_move = False
            return h.elegir_apertura(self.player_id, board, board.size)

        possible_moves = board.get_possible_moves()
        if not possible_moves:
            return (-1, -1) 

        # Verificar amenazas inmediatas
        threat_status, block_move = h.detect_and_block_imminent_win(board, self.player_id)
        if threat_status == 0:
            return block_move  # Bloquea al oponente
        elif threat_status == -1:
            return block_move  # Demasiadas amenazas, simplemente bloquea una

        best_score = float('-inf')
        best_move = possible_moves[0]  # Fallback por si ningún movimiento mejora el score

        # Priorizar puentes entre grupos
        puentes = h.detectar_puentes(board, self.player_id)
        if puentes:
            # Ordenar puentes por puntuación descendente
            puentes_ordenados = sorted(puentes, key=lambda x: x[1], reverse=True)
            possible_moves = [move for (move, _) in puentes_ordenados]

        # Ordenar por heurística combinada (CORRECCIÓN)
        scores = []
        for move in possible_moves:
            new_board = board.clone()  # Clonar el tablero
            new_board.place_piece(*move, self.player_id)  # Modificar el clon
            score = h.evaluate_board(self.player_id, self.opponent_id, new_board)  # Pasar el clon
            scores.append((move, score))
        
        possible_moves.sort(key=lambda x: -x[1])  # Ordenar por score descendente


        for move in possible_moves:
            row, col = move

            # Creamos una copia del tablero y simulamos la jugada
            new_board = board.clone()
            new_board.place_piece(row, col, self.player_id)

            # Llamamos a minimax desde el punto de vista del oponente
            score = self.minimax(new_board, self.max_depth - 1, False, float('-inf'), float('inf'))

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move

    def minimax(self, board: HexBoard, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
        """
        Algoritmo Minimax con poda Alpha-Beta.
        """
        # Condiciones terminales
        if board.check_connection(self.player_id):
            return float('inf')  # ganamos
        elif board.check_connection(self.opponent_id):
            return float('-inf')  # el oponente ganó
        elif depth == 0 or len(board.get_possible_moves()) == 0:
            return h.evaluate_board(self.player_id, self.opponent_id, board)

        if is_maximizing:
            max_eval = float('-inf')
            for move in board.get_possible_moves():
                row, col = move
                new_board = board.clone()
                new_board.place_piece(row, col, self.player_id)     # simular jugada propia
                eval = self.minimax(new_board, depth - 1, False, alpha, beta)   # probar siguiente jugada
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # poda beta
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.get_possible_moves():
                row, col = move
                new_board = board.clone()
                new_board.place_piece(row, col, self.opponent_id)   # simular jugada del contrincante
                eval = self.minimax(new_board, depth - 1, True, alpha, beta)    # probar siguiente jugada
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # poda alpha
            return min_eval


#player.py

from scipy.cluster.hierarchy import DisjointSet
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

        # Precalcular DisjointSets para jugador y oponente
        ds_jugador = h.obtener_disjointsets(board, self.player_id)
        ds_oponente = h.obtener_disjointsets(board, self.opponent_id)
        
        # Verificar amenazas inmediatas (usando ds_oponente)
        threat_status, block_move = h.detect_and_block_imminent_win(board, self.player_id, ds_oponente)
        if threat_status == 0 or threat_status == -1:
            return block_move
        
        best_score = float('-inf')
        best_move = possible_moves[0]  # Fallback por si ningún movimiento mejora el score

        # Ordenar por heurística combinada
        scores = []
        for move in possible_moves:
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)  # Modificar el clon
            ds_clon = h.clonar_disjointset(ds_jugador)
            ds_clon.add(move)
            # Conectar con vecinos en el clon
            for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                ni, nj = move[0] + di, move[1] + dj
                if 0 <= ni < new_board.size and 0 <= nj < new_board.size and new_board.board[ni][nj] == self.player_id:
                    ds_clon.merge(move, (ni, nj))
            score = h.evaluate_board(self.player_id, self.opponent_id, new_board, ds_clon)
            scores.append((move, score))
        
        possible_moves.sort(key=lambda x: -x[1])
        for move in possible_moves:
            row, col = move

            # Creamos una copia del tablero y simulamos la jugada
            new_board = board.clone()
            new_board.place_piece(row, col, self.player_id)

            # Llamamos a minimax desde el punto de vista del oponente
            score = self.minimax(new_board, self.max_depth - 1, False, float('-inf'), float('inf'), ds_jugador, ds_oponente)

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move


    def minimax(self, board: HexBoard, depth: int, is_maximizing: bool, alpha: float, beta: float, ds_jugador: DisjointSet, ds_oponente: DisjointSet) -> float:
        """
        Algoritmo Minimax con poda Alpha-Beta.
        """
        # Condiciones terminales
        if board.check_connection(self.player_id):
            return float('inf')     # ganamos
        elif board.check_connection(self.opponent_id):
            return float('-inf')    # el oponente ganó
        elif depth == 0 or len(board.get_possible_moves()) == 0:
            return h.evaluate_board(self.player_id, self.opponent_id, board, ds_jugador if is_maximizing else ds_oponente)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in board.get_possible_moves():
                row, col = move
                new_board = board.clone()
                new_board.place_piece(row, col, self.player_id)     # simular jugada propia
                # Clonar y actualizar DisjointSet
                ds_clon = h.clonar_disjointset(ds_jugador)
                ds_clon.add(move)
                for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                    ni, nj = move[0] + di, move[1] + dj
                    if new_board.board[ni][nj] == self.player_id:
                        ds_clon.merge(move, (ni, nj))
                eval = self.minimax(new_board, depth-1, False, alpha, beta, ds_clon, ds_oponente)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break   # poda beta
            return max_eval
        else:
            # Lógica similar para el oponente usando ds_oponente
            min_eval = float('inf')
            for move in board.get_possible_moves():
                row, col = move
                new_board = board.clone()
                new_board.place_piece(row, col, self.opponent_id)   # simular jugada del contrincante
                ds_clon = h.clonar_disjointset(ds_oponente)
                ds_clon.add(move)
                for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                    ni, nj = move[0] + di, move[1] + dj
                    if new_board.board[ni][nj] == self.opponent_id:
                        ds_clon.merge(move, (ni, nj))
                eval = self.minimax(new_board, depth-1, True, alpha, beta, ds_jugador, ds_clon)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break   # poda alpha
            return min_eval
#player.py

from scipy.cluster.hierarchy import DisjointSet
from board import HexBoard
from typing import Tuple
import time
from father_player import Player
import heuristics as h

class AI_Player(Player):
    def __init__(self, player_id: int, max_depth: int = 100, time_limit: float = 5.0):
        super().__init__(player_id)
        self.opponent_id = 3 - player_id  # Si eres 1, el oponente es 2; si eres 2, el oponente es 1
        self.max_depth = max_depth
        self.first_move = True
        self.start_time = 0 
        self.time_limit = time_limit
        self.best_move = None

    def play(self, board: HexBoard) -> Tuple[int, int]:
        """
        Método principal que el framework llamará para obtener el movimiento del jugador AI.
        Usa minimax hasta una profundidad determinada.
        """
        self.start_time = time.time()
        self.best_move = None  # Reiniciar en cada llamada

        if self.first_move and h.es_tablero_vacio(self.player_id ,board):
            self.first_move = False
            return h.elegir_apertura(self.player_id, board, board.size)

        possible_moves = board.get_possible_moves()
        if not possible_moves:
            return (-1, -1) 

        # Precalcular DisjointSets para jugador y oponente
        ds_jugador = h.obtener_disjointsets(board, self.player_id)
        ds_oponente = h.obtener_disjointsets(board, self.opponent_id)
        
        # Verificar amenazas inmediatas
        threat_status, block_move = h.detect_and_block_imminent_win(board, self.player_id)
        if threat_status == 0 or threat_status == -1:
            return block_move

        # Búsqueda iterativa con ordenamiento previo
        depth = 1
        ordered_moves = self.order_moves(board, possible_moves, ds_jugador)  # Ordenar movimientos iniciales
        while depth <= self.max_depth:
            try:
                self.minimax_time(board, depth, True, float('-inf'), float('inf'), ds_jugador, ds_oponente, ordered_moves)
                depth += 1
            except TimeoutError:
                break  # Tiempo agotado

        return self.best_move if self.best_move else ordered_moves[0][0]

    def order_moves(self, board: HexBoard, possible_moves: list, ds_jugador: DisjointSet) -> list:
        """Ordena movimientos por heurística para optimizar poda alfa-beta."""
        scores = []
        for move in possible_moves:
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)  # Modificar el clon
            ds_clon = h.clonar_disjointset(ds_jugador)
            ds_clon.add(move)
            # Conectar con vecinos en el clon
            for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                ni, nj = move[0] + di, move[1] + dj
                if h.valid_position((ni, nj), new_board.size) and new_board.board[ni][nj] == self.player_id:
                    ds_clon.merge(move, (ni, nj))
            score = h.evaluate_board(self.player_id, self.opponent_id, new_board, ds_clon)
            scores.append((move, score))
        
        return sorted(scores, key=lambda x: -x[1])  # Mayor a menor

    def minimax_time(self, board: HexBoard, depth: int, is_maximizing: bool, alpha: float, beta: float,
                    ds_jugador: DisjointSet, ds_oponente: DisjointSet, ordered_moves: list) -> float:
        """Minimax con control de tiempo y ordenamiento dinámico."""
        # Verificar tiempo en cada llamada
        if time.time() - self.start_time >= self.time_limit:
            raise TimeoutError()

        # Condiciones terminales
        if board.check_connection(self.player_id):
            return float('inf')
        if board.check_connection(self.opponent_id):
            return float('-inf')
        if depth == 0 or not board.get_possible_moves():
            return h.evaluate_board(self.player_id, self.opponent_id, board, ds_jugador if is_maximizing else ds_oponente)

        # Ordenar movimientos según nivel
        current_moves = [m[0] for m in ordered_moves] if depth == self.max_depth else board.get_possible_moves()
        if is_maximizing:
            current_moves.sort(key=lambda m: self.eval_move(board, m, self.player_id, ds_jugador), reverse=True)
        else:
            current_moves.sort(key=lambda m: self.eval_move(board, m, self.opponent_id, ds_oponente))

        best_val = float('-inf') if is_maximizing else float('inf')
        best_move = None

        for move in current_moves:
            # Simular movimiento
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id if is_maximizing else self.opponent_id)
            
            # Actualizar DisjointSet correspondiente
            if is_maximizing:
                ds_clon = h.clonar_disjointset(ds_jugador)
                ds_clon.add(move)
                for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                    ni, nj = move[0] + di, move[1] + dj
                    if h.valid_position((ni, nj), new_board.size) and new_board.board[ni][nj] == self.player_id:
                        ds_clon.merge(move, (ni, nj))
            else:
                ds_clon = h.clonar_disjointset(ds_oponente)
                ds_clon.add(move)
                for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
                    ni, nj = move[0] + di, move[1] + dj
                    if h.valid_position((ni, nj), new_board.size) and new_board.board[ni][nj] == self.opponent_id:
                        ds_clon.merge(move, (ni, nj))
                

            # Llamada recursiva
            eval = self.minimax_time(new_board, depth-1, not is_maximizing, alpha, beta, 
                                    ds_clon if is_maximizing else ds_jugador, 
                                    ds_clon if not is_maximizing else ds_oponente, 
                                    ordered_moves)
            
            # Actualizar mejor valor y movimiento
            if is_maximizing:
                if eval > best_val:
                    best_val = eval
                    if depth == self.max_depth:
                        self.best_move = move
                alpha = max(alpha, eval)
            else:
                if eval < best_val:
                    best_val = eval
                beta = min(beta, eval)
            
            # Poda
            if beta <= alpha:
                break

        return best_val

    def eval_move(self, board: HexBoard, move: tuple, player_id: int, ds: DisjointSet) -> float:
        """Evaluación rápida para ordenamiento (sin clonar tablero)."""
        # Lógica simplificada usando DisjointSet existente
        grupos_conectados = set()
        for di, dj in [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]:
            ni, nj = move[0] + di, move[1] + dj
            if h.valid_position((ni, nj), board.size) and board.board[ni][nj] == player_id:
                try:
                    grupos_conectados.add(ds.__getitem__((ni, nj)))
                except KeyError:
                    continue
        return len(grupos_conectados) * 10  # Priorizar conexiones
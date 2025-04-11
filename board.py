#board.py

import numpy as np
import copy
from scipy.cluster.hierarchy import DisjointSet
from itertools import product

class HexBoard:
    def __init__(self, size: int):
        self.size = size  # Tamaño N del tablero (NxN)
        self.board = [[0] * size for _ in range(size)]  # Matriz NxN (0=vacío, 1=Jugador1, 2=Jugador2)
        self.player_positions = {1: set(), 2: set()}  # Registro de fichas por jugador
        
        
    def clone(self):# -> HexBoard:
        """Devuelve una copia del tablero actual"""
        return copy.deepcopy(self)

    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        """Coloca una ficha si la casilla está vacía."""
        
        if self.board[row][col] == 0:
            self.board[row][col] = player_id
            self.player_positions[player_id].add((row, col))

    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        return [ (i,j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
    
    # def check_connection(self, player_id: int) -> bool:
    #     """Verifica si el jugador ha conectado sus dos lados"""
        
    #     visited = np.zeros((self.size, self.size), dtype=bool)
    #     x = [0 , 0, -1, -1, 1, 1]
    #     y = [-1, 1, 0, 1, -1, 0]
        
    #     def valid(x,y):
    #         return x >= 0 and x < self.size and y >= 0 and y < self.size 
        
    #     def search(row, col):
    #         visited[row][col] = True
            
    #         if (player_id == 1 and row == self.size - 1) or (player_id == 2 and col == self.size - 1):
    #             return True
            
    #         for i in range(6):
    #             new_row = row + x[i]
    #             new_col = col + y[i]
                
    #             if valid(new_row, new_col) and not visited[new_row][new_col] and self.board[new_row][new_col] == player_id: 
    #                 if search(new_row, new_col):
    #                     return True
                    
    #         visited[row][col] = False
    #         return False
        
    #     for i in range(self.size):
    #         row = 0 if player_id==1 else i
    #         col = i if player_id==1 else 0
    #         if self.board[row][col] == player_id and search(row,col):
    #             return True
            
    #     return False
    
    def print(self):
        
        print()
        
        for i in self.board:
            print(i)

    

    # def print_board(self):
    #     space = ""
    #     print(space , end="     ")
    #     for i in range(self.size):
    #         print(f"\033[31m{i}  \033[0m", end=" ")
    #     print("\n")
    #     for i in range(self.size):
    #         print(space , end=" ")
    #         print(f"\033[34m{i}  \033[0m",end=" ")
    #         for j in range(self.size):
    #             if self.board[i][j] == 0:
    #                 print("⬜ ",end=" ")
    #             if self.board[i][j] == 1:
    #                 print("🟥 ",end=" ")
    #             if self.board[i][j] == 2:
    #                 print("🟦 ",end=" ")
    #             if j == self.size -1:
    #                 print(f"\033[34m {i} \033[0m",end=" ")
    #         space += "  "
    #         print("\n")
    #     print(space,end="    ")
    #     for i in range(self.size):
    #         print(f"\033[31m{i}  \033[0m", end=" ")
            
    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados (Jugador 1: izquierda-derecha, Jugador 2: arriba-abajo)"""
        
        visited = np.zeros((self.size, self.size), dtype=bool)
        x = [0, 0, -1, -1, 1, 1]  # Movimiento en filas (direcciones verticales)
        y = [-1, 1, 0, 1, -1, 0]  # Movimiento en columnas (direcciones horizontales)
        
        def valid(x, y):
            return 0 <= x < self.size and 0 <= y < self.size
        
        def search(row, col):
            visited[row][col] = True
            
            # Jugador 1 (🔴): Verificar si llegó a la columna final (derecha)
            if player_id == 1 and col == self.size - 1:
                return True
            # Jugador 2 (🔵): Verificar si llegó a la fila final (abajo)
            elif player_id == 2 and row == self.size - 1:
                return True
            
            for i in range(6):
                new_row = row + x[i]
                new_col = col + y[i]
                if valid(new_row, new_col) and not visited[new_row][new_col] and self.board[new_row][new_col] == player_id:
                    if search(new_row, new_col):
                        return True
            visited[row][col] = False
            return False
        
        # Iniciar búsqueda desde los bordes correspondientes
        if player_id == 1:
            # Jugador 1: Comenzar desde todas las celdas de la columna 0 (izquierda)
            for row in range(self.size):
                if self.board[row][0] == player_id and search(row, 0):
                    return True
        else:
            # Jugador 2: Comenzar desde todas las celdas de la fila 0 (arriba)
            for col in range(self.size):
                if self.board[0][col] == player_id and search(0, col):
                    return True
        return False

    def print_board(self):
        space = ""
        print(space, end="     ")
        # Columnas en azul (Jugador 2, vertical)
        for i in range(self.size):
            print(f"\033[34m{i}  \033[0m", end=" ")
        print("\n")
        for i in range(self.size):
            print(space, end=" ")
            # Filas en rojo (Jugador 1, horizontal)
            print(f"\033[31m{i}  \033[0m", end=" ")
            for j in range(self.size):
                if self.board[i][j] == 0:
                    print("⬜ ", end=" ")
                elif self.board[i][j] == 1:
                    print("🟥 ", end=" ")
                else:
                    print("🟦 ", end=" ")
                if j == self.size - 1:
                    print(f"\033[31m {i} \033[0m", end=" ")
            space += "  "
            print("\n")
        print(space, end="    ")
        # Columnas finales en azul
        for i in range(self.size):
            print(f"\033[34m{i}  \033[0m", end=" ")           
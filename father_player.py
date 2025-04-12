from board import HexBoard

# Definición de la clase base Player
# Esta clase representa un jugador en el juego Hex.
class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # 1 (rojo) or 2 (azul)

    def play(self, board: "HexBoard") -> tuple:
        raise NotImplementedError("Implement this method!")
    

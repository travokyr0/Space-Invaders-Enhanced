import pygame
from game.game_manager import GameManager

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    game = GameManager()
    game.run()
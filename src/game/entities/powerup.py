import pygame
from game.settings import *
from game.utilities import load_image

# Усиления
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center_pos, type):
        super().__init__()
        self.type = type # (Все типы: 'shield', 'rapid_fire', 'life')

        if self.type == 'shield':
            self.image = load_image("assets/Sprites/Powerups/powerup_shield.png", (30, 30), CYAN, 'circle')
        elif self.type == 'rapid_fire':
             self.image = load_image("assets/Sprites/Powerups/powerup_rapidfire.png", (30, 30), MAGENTA, 'triangle')
        elif self.type == 'life':
             self.image = load_image("assets/Sprites/Powerups/powerup_life.png", (30, 30), ORANGE, 'rect')
        else:
             self.image = pygame.Surface((30,30))
             self.image.fill(WHITE)

        self.rect = self.image.get_rect(center=center_pos)
        self.speed = POWERUP_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

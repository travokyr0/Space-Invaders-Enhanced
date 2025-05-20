import pygame
from game.settings import *

def load_image(filename, size=None, fallback_color=WHITE, fallback_shape='rect'):
    try:
        image = pygame.image.load(filename).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Warning: Не удалось загрузить картинку {filename}: {e}. Использую замену.")
        if not size: size = (40, 40)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(fallback_color)
        # Отрисовка заднего фона
        center = (size[0] // 2, size[1] // 2)
        if fallback_shape == 'rect':
            pygame.draw.rect(surface, BLACK, (5, 5, size[0] - 10, size[1] - 10), 2)
        elif fallback_shape == 'circle':
            pygame.draw.circle(surface, BLACK, center, min(size) // 2 - 2, 2)
        elif fallback_shape == 'triangle':
             pygame.draw.polygon(surface, BLACK, [(center[0], 5), (5, size[1]-5), (size[0]-5, size[1]-5)], 2)
        return surface

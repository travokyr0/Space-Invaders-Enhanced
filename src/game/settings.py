SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Константы
PLAYER_SPEED = 5 # Скорость игрока
ENEMY_BASE_SPEED = 1 # Скорость врагов
ENEMY_SHOOT_COOLDOWN_BASE = 130 # КД выстрела врагов
PLAYER_INVULNERABILITY_DURATION = 120 # ФПС
PLAYER_SHIELD_DURATION = 300 # Длительность щита
PLAYER_RAPIDFIRE_DURATION = 480 # Длительность быстрого огня
PLAYER_RAPIDFIRE_COOLDOWN = 10 # КД выстрела с улучшением
PLAYER_NORMAL_SHOOT_COOLDOWN = 20 # КД обычного выстрела
ENEMY_WIDTH = 35
ENEMY_HEIGHT = 35
ENEMY_H_SPACING = 55
ENEMY_V_SPACING = 45
PLAYER_BULLET_SPEED = -10 # Скорость полета пули игрока
ENEMY_BULLET_SPEED = 5 # Скорость полета пули врага
POWERUP_SPEED = 3 # Скорость падения улучшений
POWERUP_DROP_CHANCE = 0.15 # Шанс выпада улучшений

MENU = 0
PLAYING = 1
SETTINGS = 2
GAME_OVER = 3

UI_FONT_SIZE = 36
LARGE_FONT_SIZE = 74
MENU_FONT_SIZE = 50

# Волны
# N - Обычный | S - Стреляющий | T - Танк
wave_definitions = [
    [
        ['S', 'N', 'S', 'N', 'S'],
        ['N', 'N', 'N', 'N', 'N', 'N'],
    ],
    [
        ['T', 'S', 'T', 'S', 'T'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['S', 'N', 'S', 'N', 'S', 'N', 'S'],
    ],
    [
        ['S', 'S', 'S', 'S', 'S', 'S', 'S'],
        ['T', 'N', 'T', 'N', 'T', 'N', 'T'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
    ],
    [
        ['T','T','T','T','T','T'],
        ['S', 'N', 'S', 'N', 'S', 'N', 'S', 'N'],
        ['N','N','N','N','N','N','N','N','N'],
        ['S','S','S','S','S','S','S','S'],
    ],
     [
        ['S','T','S','T','S','T','S'],
        ['T','S','T','S','T','S','T'],
        ['S','N','S','N','S','N','S','N','S'],
        ['T','T','T','T','T','T','T','T'],
    ]
]

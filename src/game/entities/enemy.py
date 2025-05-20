import pygame
import random
from game.settings import *
from game.utilities import load_image
from .bullets import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type='N'):
        super().__init__()
        self.enemy_type = enemy_type
        self.is_shooter = (enemy_type == 'S')
        self.is_tank = (enemy_type == 'T')
        self.health = 3 if self.is_tank else 1
        self.max_health = self.health

        # Типы врагов
        if self.is_shooter:
            img_file = "assets/Sprites/Enemies/enemy_shooter.png"
            color_fallback = RED
            shape_fallback = 'circle'
            self.points = 20
        elif self.is_tank:
            img_file = "assets/Sprites/Enemies/enemy_tank.png"
            color_fallback = BLUE
            shape_fallback = 'rect'
            self.points = 30
        else: # Обычный
            img_file = "assets/Sprites/Enemies/enemy.png"
            color_fallback = YELLOW
            shape_fallback = 'rect'
            self.points = 10

        self.original_image = load_image(img_file, (ENEMY_WIDTH, ENEMY_HEIGHT), color_fallback, shape_fallback)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = ENEMY_BASE_SPEED
        self.direction = 1
        self.move_down_amount = 0
        self.shoot_cooldown = random.randint(ENEMY_SHOOT_COOLDOWN_BASE // 2, ENEMY_SHOOT_COOLDOWN_BASE * 2)
        self.base_speed = ENEMY_BASE_SPEED
        self.hit_flash_timer = 0

    def update(self, wave_multiplier):
        # Повышение скорости от волн
        self.speed = self.base_speed + (wave_multiplier * 0.10)

        self.rect.x += self.speed * self.direction
        if self.move_down_amount > 0:
            self.rect.y += self.move_down_amount
            self.move_down_amount = 0

        if self.is_shooter and self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Флэш-эффект 
        if self.is_tank and self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            if self.hit_flash_timer % 10 < 5 :
                 flash_image = self.original_image.copy()
                 flash_image.fill(WHITE, special_flags=pygame.BLEND_RGB_ADD)
                 self.image = flash_image
            else:
                 self.image = self.original_image
            if self.hit_flash_timer == 0:
                 self.image = self.original_image
        elif self.image != self.original_image and self.hit_flash_timer <= 0 :
             self.image = self.original_image


    def shoot(self):
        if self.is_shooter:
            # if enemy_laser_sound: enemy_laser_sound.play()
            self.shoot_cooldown = random.randint(ENEMY_SHOOT_COOLDOWN_BASE, ENEMY_SHOOT_COOLDOWN_BASE * 3)
            return EnemyBullet(self.rect.centerx, self.rect.bottom)
        return None

    def trigger_move_down(self, amount):
        self.move_down_amount = amount

    def take_damage(self, amount):
        if self.is_tank:
            self.health -= amount
            if self.health > 0:
                self.hit_flash_timer = 20
                return False
        self.kill()
        return True

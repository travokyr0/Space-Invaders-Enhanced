import pygame
from game.settings import *
from game.utilities import load_image
from game.entities.bullets import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image("assets/Sprites/player.png", (40, 40), GREEN, 'triangle')
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.shoot_cooldown = 0
        self.last_shot_time = 0

        # Усилители
        self.shield_active = False
        self.shield_timer = 0
        self.shield_image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.shield_image, CYAN + (100,), (30, 30), 30, 3)

        self.rapid_fire_active = False
        self.rapid_fire_timer = 0


    def update(self, keys):
        # Передвижение
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

        # Задержка выстрела
        current_time = pygame.time.get_ticks()
        if self.shoot_cooldown > 0:
             self.shoot_cooldown -= 1

        # Неуязвимость
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.image = self.original_image
            else:
                alpha = 100 if (current_time // 100) % 2 == 0 else 255
                temp_image = self.original_image.copy()
                temp_image.set_alpha(alpha)
                self.image = temp_image
        elif not self.shield_active:
             if self.image != self.original_image:
                  self.image = self.original_image

        # Щит
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                if not self.invulnerable:
                     self.image = self.original_image

        # Быстрый выстрел
        if self.rapid_fire_active:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False


    def can_shoot(self):
        if self.rapid_fire_active:
            return self.shoot_cooldown <= 0
        else:
            now = pygame.time.get_ticks()
            return now - self.last_shot_time >= (1000 / (60/PLAYER_NORMAL_SHOOT_COOLDOWN)) # Конвертация задержки в мс


    def shoot(self):
        if self.can_shoot():
            # if laser_sound: laser_sound.play()
            if self.rapid_fire_active:
                self.shoot_cooldown = PLAYER_RAPIDFIRE_COOLDOWN
            else:
                self.last_shot_time = pygame.time.get_ticks()

            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield_active:
            shield_rect = self.shield_image.get_rect(center=self.rect.center)
            surface.blit(self.shield_image, shield_rect)


    def gain_life(self, amount=1):
        self.lives += amount
        print(f"Получена жизнь! Жизней: {self.lives}")

    def reset_position(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.invulnerable = False
        self.shield_active = False
        self.rapid_fire_active = False
        self.image = self.original_image

    def make_invulnerable(self, duration=PLAYER_INVULNERABILITY_DURATION):
        if not self.shield_active:
            self.invulnerable = True
            self.invulnerable_timer = duration
            self.image = self.original_image.copy()

    def activate_shield(self):
        print("Щит активирован!")
        self.shield_active = True
        self.shield_timer = PLAYER_SHIELD_DURATION
        self.invulnerable = False
        self.image = self.original_image

    def activate_rapid_fire(self):
        print("Скорострельность активирована!")
        self.rapid_fire_active = True
        self.rapid_fire_timer = PLAYER_RAPIDFIRE_DURATION
        self.shoot_cooldown = 0

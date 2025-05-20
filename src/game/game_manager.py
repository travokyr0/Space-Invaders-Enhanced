import pygame
import os
import random
from game.settings import *
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.entities.bullets import *
from game.entities.powerup import PowerUp

class GameManager:
    def __init__(self):

        # Инициализация шрифтов
        self.UI_FONT = pygame.font.Font("assets/Fonts/PixelizerBold.ttf", UI_FONT_SIZE)
        self.LARGE_FONT = pygame.font.Font("assets/Fonts/PixelizerBold.ttf", LARGE_FONT_SIZE)
        self.MENU_FONT = pygame.font.Font("assets/Fonts/PixelizerBold.ttf", MENU_FONT_SIZE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Enhanced")

        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()
        self.wave = 0
        self.wave_definitions = wave_definitions
        self.highscore = self.load_highscore()

        self.game_state = MENU
        self.game_over_message = "ИГРА ОКОНЧЕНА"

        self.play_button_rect = None
        self.settings_button_rect = None
        self.exit_button_rect = None
        self.back_button_rect = None

        self.esc_hold_start_time = None
        self.esc_hold_duration_ms = 1500 # 3 секунды в миллисекундах

    def load_highscore(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read().strip())
            else:
                return 0
        except (ValueError, IOError) as e:
            print(f"Ошибка загрузки рекорда: {e}. Сброс на 0.")
            return 0

    def save_highscore(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.highscore))
        except IOError as e:
            print(f"Ошибка сохранения рекорда: {e}")


    def start_new_game(self):
        self.player.lives = 3
        self.player.score = 0
        self.player.reset_position()
        self.wave = 0
        self.paused = False

        # Очистка всех групп
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.powerups.empty()
        self.all_sprites.empty()

        self.all_sprites.add(self.player)

        # Начало первой волны
        self.next_wave()
        self.game_state = PLAYING
        # if mixer.music:
        #     mixer.music.stop()
        #     mixer.music.play(-1)


    def create_wave(self, wave_index):
        # Очистка всего от прошлой волны
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.powerups.empty()


        if wave_index >= len(self.wave_definitions):
            print(f"Предупреждение: Волна {wave_index + 1} не определена. Используется последняя.")
            wave_layout = self.wave_definitions[-1]
        else:
            wave_layout = self.wave_definitions[wave_index]

        if not wave_layout:
            print(f"Предупреждение: Определение волны {wave_index + 1} пустое.")
            return

        max_cols = max(len(row) for row in wave_layout) if wave_layout else 0
        if max_cols == 0: return

        formation_width = (max_cols * ENEMY_WIDTH) + ((max_cols - 1) * (ENEMY_H_SPACING - ENEMY_WIDTH))
        start_x_offset = (SCREEN_WIDTH - formation_width) // 2
        start_y = 60

        current_y = start_y
        for row_layout in wave_layout:
            num_cols_in_row = len(row_layout)
            if num_cols_in_row == 0: continue

            row_width = (num_cols_in_row * ENEMY_WIDTH) + ((num_cols_in_row - 1) * (ENEMY_H_SPACING - ENEMY_WIDTH))
            row_start_x = start_x_offset + (formation_width - row_width) // 2

            for i, enemy_type in enumerate(row_layout):
                x = row_start_x + i * ENEMY_H_SPACING
                y = current_y
                enemy = Enemy(x, y, enemy_type)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            current_y += ENEMY_V_SPACING


    def next_wave(self):
        self.wave += 1
        print(f"Начало Волны {self.wave}")
        self.display_wave_message()
        self.create_wave(self.wave - 1)
        self.player.make_invulnerable(60)


    def display_wave_message(self):
        self.screen.fill(BLACK)
        wave_text_surf = self.LARGE_FONT.render(f"Волна {self.wave}", True, YELLOW)
        wave_text_rect = wave_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(wave_text_surf, wave_text_rect)
        pygame.display.flip()
        pygame.time.wait(1500)


    def check_collisions(self):
        # Попадание пули
        enemy_hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        for bullet, hit_enemies in enemy_hits.items():
             for enemy in hit_enemies:
                 if enemy.take_damage(1):
                     # if explosion_sound: explosion_sound.play()
                     self.player.score += enemy.points

                     # Шанс на выпадение усилителя
                     if random.random() < POWERUP_DROP_CHANCE:
                         self.spawn_powerup(enemy.rect.center)

                     if len(self.enemies) == 0:
                         self.next_wave()
                         return


        if not self.player.invulnerable and not self.player.shield_active:
            player_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if player_hits:
                self.player_hit()

        if not self.player.invulnerable and not self.player.shield_active:
            enemy_player_collision = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if enemy_player_collision:
                for enemy in enemy_player_collision:
                    enemy.kill()
                    self.player.score += 5
                self.player_hit()

                if len(self.enemies) == 0:
                    self.next_wave()
                    return

        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in collected_powerups:
            # if powerup_sound: powerup_sound.play()
            if powerup.type == 'shield':
                self.player.activate_shield()
            elif powerup.type == 'rapid_fire':
                self.player.activate_rapid_fire()
            elif powerup.type == 'life':
                self.player.gain_life()

    def player_hit(self):
        # if explosion_sound: explosion_sound.play()
        self.player.lives -= 1
        print(f"Игрок подбит! Жизней осталось: {self.player.lives}")
        if self.player.lives <= 0:
            self.trigger_game_over()
        else:
            self.player.make_invulnerable()


    def spawn_powerup(self, position):
        powerup_type = random.choice(['shield', 'rapid_fire', 'life'])

        new_powerup = PowerUp(position, powerup_type)
        self.powerups.add(new_powerup)
        self.all_sprites.add(new_powerup)


    def handle_enemy_actions(self):
        move_down = False
        direction_change = 1
        for enemy in self.enemies:
            if enemy.rect.right > SCREEN_WIDTH - 10:
                direction_change = -1
                move_down = True
            elif enemy.rect.left < 10:
                direction_change = 1
                move_down = True
            # Проверка если враги достигли нижнего края
            if enemy.rect.bottom >= SCREEN_HEIGHT - 60:
                self.trigger_game_over("Захватчики достигли нижнего края!")
                return

        if move_down:
            for enemy in self.enemies:
                enemy.direction = direction_change
                enemy.trigger_move_down(15)

        shooters_ready = [e for e in self.enemies if e.is_shooter and e.shoot_cooldown <= 0]
        shooting_probability = 0.01 + (self.wave * 0.0025)

        for enemy in shooters_ready:
            # Стрельба врагов
            player_x = self.player.rect.centerx
            if abs(enemy.rect.centerx - player_x) < SCREEN_WIDTH / 4:
                 if random.random() < shooting_probability:
                     bullet = enemy.shoot()
                     if bullet:
                         self.enemy_bullets.add(bullet)
                         self.all_sprites.add(bullet)


    def trigger_game_over(self, message="ИГРА ОКОНЧЕНА"):
        print(f"Игра окончена: {message}")
        self.game_over_message = message
        self.game_state = GAME_OVER
        # if mixer.music: mixer.music.stop()
        if self.player.score > self.highscore:
            print(f"Новый рекорд: {self.player.score}")
            self.highscore = self.player.score
            self.save_highscore()


    def draw_text(self, text, font, color, surface, x, y, center=False):
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        if center:
            textrect.center = (x, y)
        else:
            textrect.topleft = (x, y)
        surface.blit(textobj, textrect)
        return textrect


    def draw_menu(self):
        self.screen.fill(BLACK)
        self.draw_text('Space Invaders Enhanced', self.LARGE_FONT, YELLOW, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2, center=True)
        self.draw_text(f'Рекорд: {self.highscore}', self.UI_FONT, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.35, center=True)

        # Отрисовка кнопок главного меню
        self.play_button_rect = self.draw_text('Играть [Enter]', self.MENU_FONT, GREEN, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.55, center=True)
        self.settings_button_rect = self.draw_text('Настройки [S]', self.MENU_FONT, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.67, center=True)
        self.exit_button_rect = self.draw_text('Выход [Q/Esc]', self.MENU_FONT, RED, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.79, center=True)

        pygame.display.flip()

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.start_new_game()
            if event.key == pygame.K_s:
                self.game_state = SETTINGS
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
             mouse_pos = event.pos
             if self.play_button_rect and self.play_button_rect.collidepoint(mouse_pos):
                 self.start_new_game()
             elif self.settings_button_rect and self.settings_button_rect.collidepoint(mouse_pos):
                 self.game_state = SETTINGS
             elif self.exit_button_rect and self.exit_button_rect.collidepoint(mouse_pos):
                 self.running = False

    def draw_settings(self):
         self.screen.fill(BLACK)
         self.draw_text('Настройки', self.LARGE_FONT, YELLOW, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2, center=True)
         # Добавление настроек
         self.draw_text('Громкость: (не реализовано)', self.UI_FONT, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.4, center=True)

         self.back_button_rect = self.draw_text('Назад [Esc]', self.MENU_FONT, ORANGE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7, center=True)
         pygame.display.flip()

    def handle_settings_input(self, event):
         if event.type == pygame.KEYDOWN:
             if event.key == pygame.K_ESCAPE:
                 self.game_state = MENU
         elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
              if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                  self.game_state = MENU


    def display_game_over(self):
        self.screen.fill(BLACK)
        self.draw_text(self.game_over_message, self.LARGE_FONT, RED, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, center=True)
        self.draw_text(f"Ваш счёт: {self.player.score}", self.UI_FONT, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        self.draw_text(f"Рекорд: {self.highscore}", self.UI_FONT, YELLOW, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)
        self.draw_text("Нажмите 'R' для рестарта или 'M'/'Q' для выхода в меню", self.UI_FONT, GREEN, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, center=True)
        pygame.display.flip()

    def handle_game_over_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_m:
                self.game_state = MENU
            if event.key == pygame.K_r:
                self.start_new_game()


    def display_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        self.draw_text("ПАУЗА", self.LARGE_FONT, YELLOW, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, center=True)
        self.draw_text("Нажмите 'P' для продолжения", self.UI_FONT, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, center=True)
        self.draw_text("Нажмите 'M' для выхода в меню", self.UI_FONT, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, center=True)
        pygame.display.flip()


    def draw_ui(self):
        # Отображение жизней
        self.draw_text(f"Жизни: {self.player.lives}", self.UI_FONT, WHITE, self.screen, 10, 5)
        # Отображение очков
        score_surf = self.UI_FONT.render(f"Счёт: {self.player.score}", True, WHITE)
        score_rect = score_surf.get_rect(topright=(SCREEN_WIDTH - 10, 5))
        self.screen.blit(score_surf, score_rect)
        # Отображение волны
        self.draw_text(f"Волна: {self.wave}", self.UI_FONT, YELLOW, self.screen, SCREEN_WIDTH // 2, 20, center=True)

        # Таймеры усилителей
        if self.player.shield_active:
            self.draw_text(f"Щит: {self.player.shield_timer // 60 + 1}с", self.UI_FONT, CYAN, self.screen, 10, SCREEN_HEIGHT - 40)
        if self.player.rapid_fire_active:
             self.draw_text(f"Огонь!: {self.player.rapid_fire_timer // 60 + 1}с", self.UI_FONT, MAGENTA, self.screen, 150, SCREEN_HEIGHT - 40)


    def run(self):
        while self.running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # Отслеживание ивентов
                if self.game_state == MENU:
                    self.handle_menu_input(event)
                elif self.game_state == SETTINGS:
                    self.handle_settings_input(event)
                elif self.game_state == GAME_OVER:
                    self.handle_game_over_input(event)
                elif self.game_state == PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                            # if self.paused and mixer.music: mixer.music.pause()
                            # elif not self.paused and mixer.music: mixer.music.unpause()
                        elif event.key == pygame.K_m and self.paused:
                            self.paused = False
                            # if mixer.music: mixer.music.stop()
                            self.game_state = MENU


            # Отрисовка
            if self.game_state == MENU:
                self.draw_menu()
            elif self.game_state == SETTINGS:
                self.draw_settings()
            elif self.game_state == GAME_OVER:
                self.display_game_over()
            elif self.game_state == PLAYING:

                # Проверка удержания Esc для выхода
                current_time_ms = pygame.time.get_ticks()
                if keys[pygame.K_ESCAPE]:
                    if self.esc_hold_start_time is None:
                        # Начало удержания Esc
                        self.esc_hold_start_time = current_time_ms
                        print("Начато удержание Esc для выхода...")
                    else:
                        # Esc уже удерживается, проверяем время
                        held_time = current_time_ms - self.esc_hold_start_time
                        if held_time >= self.esc_hold_duration_ms:
                            print(f"Esc удерживался {self.esc_hold_duration_ms / 1000} сек. Выход...")
                            self.running = False
                        # Можно добавить визуальный индикатор удержания здесь
                else:
                    # Esc не нажат, сбрасываем таймер, если он был запущен
                    if self.esc_hold_start_time is not None:
                        print("Удержание Esc прервано.")
                        self.esc_hold_start_time = None
                if self.paused:
                    self.display_pause()
                else:
                    self.player.update(keys)
                    self.enemies.update(self.wave)
                    self.bullets.update()
                    self.enemy_bullets.update()
                    self.powerups.update()

                    # Выстрел игрока
                    if keys[pygame.K_SPACE]:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.add(bullet)
                            self.all_sprites.add(bullet)

                    self.handle_enemy_actions()
                    if not self.running: continue

                    self.check_collisions()
                    if not self.running: continue

                    # Отрисовка заднего фона
                    self.screen.fill(BLACK)

                    for sprite in self.all_sprites:
                        if sprite == self.player:
                            self.player.draw(self.screen)
                        else:
                            self.screen.blit(sprite.image, sprite.rect)

                    self.draw_ui()
                    pygame.display.flip()

            # Контроль ФПС
            self.clock.tick(60)

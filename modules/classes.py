import pygame
import os
from modules.mapsetting import map

# Основные настройки
PATH = os.path.abspath(__file__ + '/../..')
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
STEP = 50
# Звуки и музыка
is_paused = False
# Инициализация
pygame.init()
# Инициализация микшера для музыки и звуков
pygame.mixer.init()
# Фоновая музыка
pygame.mixer.music.load(os.path.join(PATH, 'sounds/back_music.wav'))
pygame.mixer.music.play(-1)  # -1 означает бесконечное повторение
pygame.mixer.music.set_volume(0.5)  # Уровень громкости (от 0 до 1)
# Звуки выстрела и попадания
shot_sound = pygame.mixer.Sound(os.path.join(PATH, 'sounds/shot.wav'))
strike_sound = pygame.mixer.Sound(os.path.join(PATH, 'sounds/strike.wav'))
shot_sound.set_volume(0.5)
strike_sound.set_volume(0.5)

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tanks 2D')

background = pygame.image.load(os.path.join(PATH, 'images/background.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

font = pygame.font.Font(None, 120)
winner1_text = font.render('BLUE WIN', True, (0, 0, 255))
winner2_text = font.render('RED WIN', True, (255, 0, 0))

pause_font = pygame.font.Font(None, 100)
pause_text = pause_font.render('PAUSED', True, (255, 255, 255))

# Загрузка стен
wall_image1 = os.path.join(PATH, 'images/wall.png')
wall_image2 = os.path.join(PATH, 'images/wall1.png')

x = 0
y = 0
blocks_list = []


def draw_volume_bar():
    volume = pygame.mixer.music.get_volume()
    bar_width = 200
    bar_height = 20
    bar_x = 10
    bar_y = 10
    # Фон полоски (пустая часть)
    pygame.draw.rect(window, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
    # Заполненная часть полоски
    pygame.draw.rect(window, (0, 255, 0), (bar_x, bar_y, bar_width * volume, bar_height))
    # Рамка
    pygame.draw.rect(window, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)


class Block(pygame.Rect):
    def __init__(self, x, y, type_block, image):
        super().__init__(x, y, STEP, STEP)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (STEP, STEP))
        self.type_block = type_block
        self.is_destroyed = False  # Новый флаг разрушения
        self.damage_image = pygame.image.load(os.path.join(PATH, 'images/damage.png'))
        self.damage_image = pygame.transform.scale(self.damage_image, (STEP, STEP))

    def blit(self):
        if self.is_destroyed:
            window.blit(self.damage_image, (self.x, self.y))
        else:
            window.blit(self.image, (self.x, self.y))

    def damage(self):
        self.is_destroyed = True


for row in map:
    for i in row:
        if i == 1:
            blocks_list.append(Block(x, y, 1, wall_image1))
        elif i == 2:
            blocks_list.append(Block(x, y, 2, wall_image2))
        x += STEP
    y += STEP
    x = 0


class Bullet(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.image = pygame.image.load(os.path.join(PATH, 'images/bullet.png'))
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.direction = None
        self.speed = 20  # Пули летят быстро
        self.active = False  # Теперь вместо count будет active

    def move(self):
        if self.active:
            window.blit(self.image, (self.x, self.y))
            if self.direction == 0:
                self.y -= self.speed
            elif self.direction == 180:
                self.y += self.speed
            elif self.direction == 90:
                self.x -= self.speed
            elif self.direction == 270:
                self.x += self.speed

            # Ограничение по экрану
            if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
                self.stop()

    def stop(self):
        self.active = False
        self.x = -1000
        self.y = -1000


class Panzar(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x * STEP, y * STEP, STEP, STEP)
        self.image = None
        self.pos = [x, y]
        self.bullet = Bullet(x, y)
        self.angle = 0
        self.is_alive = True

    def move(self):
        pass

    def blit(self):
        if self.is_alive:
            window.blit(self.image, (self.x, self.y))
        else:
            kill_image = pygame.image.load(os.path.join(PATH, 'images/kill.png'))
            kill_image = pygame.transform.scale(kill_image, (STEP, STEP))
            window.blit(kill_image, (self.x, self.y))

    def rotate_to(self, angle):
        rotate = (360 - self.angle + angle)
        self.angle = angle
        self.image = pygame.transform.rotate(self.image, rotate)

    def strike(self):
        if not self.bullet.active:
            self.bullet.x = self.x + STEP / 2 - 10
            self.bullet.y = self.y + STEP / 2 - 10
            self.bullet.active = True
            self.bullet.direction = self.angle
            shot_sound.play()  # <<< добавили звук выстрела

    def check_collision(self, bullet):
        if self.colliderect(bullet):
            self.is_alive = False
            bullet.stop()
            strike_sound.play()  # <<< добавили звук удара


class Player(Panzar):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load(os.path.join(PATH, 'images/panzer.png'))
        self.image = pygame.transform.scale(self.image, (STEP, STEP))

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            if map[self.pos[1] - 1][self.pos[0]] == 0:
                self.y -= STEP
                self.pos[1] -= 1
            self.rotate_to(0)
        elif keys[pygame.K_s]:
            if map[self.pos[1] + 1][self.pos[0]] == 0:
                self.y += STEP
                self.pos[1] += 1
            self.rotate_to(180)
        elif keys[pygame.K_a]:
            if map[self.pos[1]][self.pos[0] - 1] == 0:
                self.x -= STEP
                self.pos[0] -= 1
            self.rotate_to(90)
        elif keys[pygame.K_d]:
            if map[self.pos[1]][self.pos[0] + 1] == 0:
                self.x += STEP
                self.pos[0] += 1
            self.rotate_to(270)
        # elif keys[pygame.K_z]:
        #     self.strike()


class Player2(Panzar):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load(os.path.join(PATH, 'images/enemy.png'))
        self.image = pygame.transform.scale(self.image, (STEP, STEP))

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if map[self.pos[1] - 1][self.pos[0]] == 0:
                self.y -= STEP
                self.pos[1] -= 1
            self.rotate_to(0)
        elif keys[pygame.K_DOWN]:
            if map[self.pos[1] + 1][self.pos[0]] == 0:
                self.y += STEP
                self.pos[1] += 1
            self.rotate_to(180)
        elif keys[pygame.K_LEFT]:
            if map[self.pos[1]][self.pos[0] - 1] == 0:
                self.x -= STEP
                self.pos[0] -= 1
            self.rotate_to(90)
        elif keys[pygame.K_RIGHT]:
            if map[self.pos[1]][self.pos[0] + 1] == 0:
                self.x += STEP
                self.pos[0] += 1
            self.rotate_to(270)
        # elif keys[pygame.K_x]:
        #     self.strike()


# Создание игроков
player1 = Player(1, 1)
player2 = Player2(1, 3)
clock = pygame.time.Clock()

# Основной игровой цикл
is_game_running = True
winner = None
is_winner = False

while is_game_running:
    window.blit(background, (0, 0))

    if not is_paused:
        # Всё, что должно происходить ТОЛЬКО если игра НЕ на паузе
        for block in blocks_list:
            block.blit()

            if block.colliderect(player1.bullet):
                player1.bullet.stop()
                if block.type_block == 1 and not block.is_destroyed:
                    block.damage()
                    map[block.y // STEP][block.x // STEP] = 0

            if block.colliderect(player2.bullet):
                player2.bullet.stop()
                if block.type_block == 1 and not block.is_destroyed:
                    block.damage()
                    map[block.y // STEP][block.x // STEP] = 0

        player1.bullet.move()
        player2.bullet.move()
        player1.move()
        player2.move()

        player1.blit()
        player2.blit()

        if player1.is_alive and player2.bullet.active:
            player1.check_collision(player2.bullet)
            if not player1.is_alive:
                winner = 2
                is_game_running = False
                is_winner = True

        if player2.is_alive and player1.bullet.active:
            player2.check_collision(player1.bullet)
            if not player2.is_alive:
                winner = 1
                is_game_running = False
                is_winner = True

        # ПРОВЕРКА НАЖАТЫХ КЛАВИШ (стрельба)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            player1.strike()

        if keys[pygame.K_x]:
            player2.strike()

    # События происходят всегда
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_game_running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(min(1.0, volume + 0.1))

            if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(max(0.0, volume - 0.1))

            if event.key == pygame.K_p:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

            if event.key == pygame.K_ESCAPE:
                is_paused = not is_paused

    # Рисуем полоску громкости
    draw_volume_bar()

    if is_paused:
        pause_cors = (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                      SCREEN_HEIGHT // 2 - pause_text.get_height() // 2)
        window.blit(pause_text, pause_cors)

    clock.tick(10)
    pygame.display.flip()

# Экран победы
cors = (SCREEN_WIDTH // 2 - winner1_text.get_width() // 2,
        SCREEN_HEIGHT // 2 - winner1_text.get_height() // 2)
while is_winner:
    window.blit(background, (0, 0))
    if winner == 1:
        window.blit(winner1_text, cors)
    elif winner == 2:
        window.blit(winner2_text, cors)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_winner = False

    pygame.display.flip()

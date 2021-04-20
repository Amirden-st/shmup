# Pygame шаблон - скелет для нового проекта Pygame
import pygame
import random
import os

img_dir = os.path.join(os.path.dirname(__file__), 'img')
meteor_img_dir = os.path.join(img_dir, 'meteors')

WIDTH = 480
HEIGHT = 600
FPS = 60

# задаём цвета
BACKGROUND_COLOR = (33, 33, 33)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# создание окна игры
pygame.init()
pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Shmup')
clock = pygame.time.Clock()

# собственные объекты
font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
    


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 22
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0

    def update(self, *args, **kwargs) -> None:
        self.speed_x = 0
        key_state = pygame.key.get_pressed()
        if key_state[pygame.K_LEFT]:
            self.speed_x -= 8
        elif key_state[pygame.K_RIGHT]:
            self.speed_x += 8
        self.rect.x += self.speed_x

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * .85 // 2
        self._generate()
        """
        Для создания врашения астероидам мы задаём три нижних св-ва 
        1-ое вспомогательное
        2-ое означает градус поворота
        3-ее для задания частоты поворотов 
        """
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self, *args, **kwargs) -> None:
        self._rotate()
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top > HEIGHT + 10 or self.rect.right < 0 or self.rect.left > WIDTH:
            self._generate()

    def _generate(self):
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_x = random.randrange(-3, 3)
        self.speed_y = random.randrange(1, 8)

    def _rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            """
            После того как мы назначаем на место self.image новую картинку(повернутую на self.rot градусов self.image),
            rect спрайта, оказывется неправильным, поэтому мы высчитываем новый прямоугольник на основе текущей 
            картинки, а затем ставим его на место (присваеваем ему центер старого) предыдущего спрайта
            """
            old_rect = self.rect
            self.rect = self.image.get_rect()
            self.rect.center = old_rect.center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self, *args, **kwargs) -> None:
        self.rect.y += self.speed_y

        # Убиваем объект, если он за пределами экрана
        if self.rect.bottom < 0:
            self.kill()


# Загрузка всей игровой графики
background = pygame.image.load(os.path.join(img_dir, 'background.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_dir, 'ship.png')).convert()
bullet_img = pygame.image.load(os.path.join(img_dir, 'bullet.png')).convert()

meteor_images_titles = [
    'bigBlueMeteor.png',
    'blueMeteor.png',
    'brownMeteor.png',
    'smallBrownMeteor.png',
    'verySmallBrownMeteor.png'
]

meteor_images = []

for img in meteor_images_titles:
    meteor_images.append(pygame.image.load(os.path.join(meteor_img_dir, img)).convert())

# Создание груп спрайтов и самих спрайтов
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

mobs = pygame.sprite.Group()

bullets = pygame.sprite.Group()
for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

score = 0

# game cycle
running = True
while running:
    """
    Команда tick() просит pygame определить, сколько занимает цикл, а затем сделать паузу, чтобы цикл (целый кадр) 
    длился нужное время. Если задать значение FPS 30, это значит, что длина одного кадра — 1/30, то есть 0,03 секунды. 
    Если цикл кода (обновление, рендеринг и прочее) занимает 0,01 секунды, тогда pygame сделает паузу на 0,02 секунды.
    """
    clock.tick(FPS)

    # Обходим все события произошедшие в предыдущем кадре
    for event in pygame.event.get():
        # Проверяем, не нажал ли игрок крест. Если нажал то, выходим из цикла
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Обновления
    all_sprites.update()

    # проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, False,
                                       pygame.sprite.collide_circle)  # список спрайтов, которые столкрулись с игроком
    """
    pygame.sprite.collide_rect() используется по умолчанию 4 аргументом в pygame.sprite.spritecollide() - 
    это означает, что столкновения будут измеряться с помощью кругов спрайтов, высчитываемых с помощью св-ва radius,
    а не с помощью их прямоугольников  
    """
    if hits:
        running = False

    # проверка на поподание пули в моба
    bullet_hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    """
    groupcollide() сравнивает положение груп и возвращает список задетых мобов
    """
    for mob in bullet_hits:
        print(mob.radius)
        score += 52 - mob.radius
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # Рендеринг
    # рисуем сзади "доски"
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background, background_rect)
    """
    blit — это олдскульный термин из компьютерной графики, который обозначает прорисовку пикселей одного изображения
    на другом. В этом случае — прорисовку фона на экране. Теперь фон выглядит намного лучше:
    """
    all_sprites.draw(screen)
    draw_text(screen, str(score), 23, WIDTH/2, 10)
    # поворачиваем "доску"
    pygame.display.flip()

pygame.quit()

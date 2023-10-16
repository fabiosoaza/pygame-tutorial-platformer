import pygame
from pygame.locals import *
import random
import time

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
HARD = 7
PLAYER_SIZE=30
COIN_SIZE=PLAYER_SIZE//2
MAX_TRIES_GENERATE_RANDON_PLATFORM=10

YELLOW=(255, 255, 0)
BLACK=(0, 0, 0)
RED=(255, 0, 0)
GREEN=(0, 255, 0)
BLUE=(0, 0, 255)

FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.surf.fill(BLUE)
        self.rect = self.surf.get_rect()
        self.pos = vec((10, 385))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False
        self.score = 0


    def move(self):
        self.acc = vec(0, 0.5)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[pygame.K_RIGHT]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # warp between screens
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def update(self):
        hits = pygame.sprite.spritecollide(self ,platforms, False)
        if self.vel.y > 0:
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    if hits[0].point == True:   ##
                        hits[0].point = False   ##
                        self.score += 1         ##
                    self.pos.y = hits[0].rect.top +1
                    self.vel.y = 0
                    self.jumping = False

    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((random.randint(50, 100), 12))
        self.surf.fill(GREEN)
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 30)))
        self.speed = random.randint(-1, 1)
        self.moving = True
        self.point = True   ##

    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving == True:
            self.rect.move_ip(self.speed,0)
            # moves player with platform
            if hits:
                P1.pos += (self.speed, 0)
            # warps platform if outbounds screen
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH

    # generate coin above stationary platform
    def generateCoin(self):
        if (self.speed == 0):
            coins.add(Coin((self.rect.centerx, self.rect.centery - 50)))


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.surf = pygame.Surface((COIN_SIZE, COIN_SIZE))
        self.surf.fill(YELLOW)
        self.rect = self.surf.get_rect()

        self.rect.topleft = pos

    def update(self):
        if self.rect.colliderect(P1.rect):
            P1.score += 5
            self.kill()


def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 50) and (
                    abs(platform.rect.bottom - entity.rect.top) < 50):
                return True
    return False


def generate_platforms():
    while len(platforms) < HARD:
        p = generate_platform()
        platforms.add(p)
        all_sprites.add(p)


def generate_platform():
    width = random.randrange(50, 100)
    p = None
    C = True
    tries = 0
    while C:
        p = Platform()
        p.rect.center = (random.randrange(0, WIDTH - width),
                         random.randrange(-50, 0))
        # check if is overlapping
        C = check(p, platforms)
        if tries >= MAX_TRIES_GENERATE_RANDON_PLATFORM and C is True:
            # if random generated platform is still overlapping after MAX_TRIES_GENERATE_RANDON_PLATFORM times
            upper_plat = upper_platform()
            y = upper_plat.rect.y - 50
            p.rect.center = (random.randrange(0, WIDTH - width), y)
            C = False

        tries += 1


    p.generateCoin()
    return p


def upper_platform():
    upper_platform = platforms.sprites()[0]
    for plat in platforms:
        if plat != upper_platform and plat.rect.y < upper_platform.rect.y:
            upper_platform = plat
    return upper_platform


P1 = Player()
PT1 = Platform()

PT1.moving = False
PT1.point = False

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)

PT1.surf = pygame.Surface((WIDTH, 20))
PT1.surf.fill(RED)
PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))

platforms = pygame.sprite.Group()
platforms.add(PT1)
all_sprites.add(PT1)

coins = pygame.sprite.Group()



for x in range(random.randint(4,5)):
    C = True
    pl = Platform()
    while C:
        pl = Platform()
        C = check(pl, platforms)
    pl.generateCoin()    # <----------------
    platforms.add(pl)
    all_sprites.add(pl)

font = pygame.font.SysFont("Verdana", 20)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                P1.cancel_jump()
    # game over
    if P1.rect.top > HEIGHT:
        for entity in all_sprites:
            entity.kill()
        time.sleep(0.5)
        displaysurface.fill(RED)
        pygame.display.update()
        time.sleep(1)
        run=False

    if P1.rect.top <= HEIGHT / 3:
        P1.pos.y += abs(P1.vel.y)
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()
        for coin in coins:
            coin.rect.y += abs(P1.vel.y)
            if coin.rect.top >= HEIGHT:
                coin.kill()

    displaysurface.fill(BLACK)
    g  = font.render(str(P1.score), True, YELLOW)
    displaysurface.blit(g, (WIDTH/2, 10))

    generate_platforms()
    P1.update()

    for entity in all_sprites:
        entity.move()
        displaysurface.blit(entity.surf, entity.rect)

    for coin in coins:
        displaysurface.blit(coin.surf, coin.rect)
        coin.update()

    pygame.display.update()
    FramePerSec.tick(FPS)

pygame.quit()

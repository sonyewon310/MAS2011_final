import pygame
import random
import os
from os import path

current_path = os.path.dirname(__file__)
assets_path = os.path.join(current_path, 'final_assets')
img_path = os.path.join(assets_path, 'img')
snd_path = os.path.join(assets_path, 'snd')

WIDTH = 700
HEIGHT = 500
FPS = 60
POWERUP_TIME = 5000

BROWN = (114, 74, 56)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snack Time! by YewonSon")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BROWN)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newgerm():
    g = Germ()
    all_sprites.add(g)
    germs.add(g)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

class Mouth(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(mouth_img, (250, 250))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 30
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT / 3
        

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 50))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 5
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                random_snack = random.choice(snack_list)
                snack = Snack(self.rect.centerx, self.rect.top)
                all_sprites.add(snack)
                snacks.add(snack)
                shoot_sound.play()
            if self.power >= 2:
                random_snacks = random.sample(snack_list, 2)
                snack1 = Snack(self.rect.left, self.rect.centery)
                snack2 = Snack(self.rect.right, self.rect.centery)
                all_sprites.add(snack1)
                all_sprites.add(snack2)
                snacks.add(snack1)
                snacks.add(snack2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Germ(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(germ_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.bottom = random.randrange(-80, -20)
        self.speedy = random.randrange(-3, 3)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 2)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Snack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(snack_images)
        self.image = self.image_orig.copy()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            eating_sound.play()
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['medicine', 'capsules'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Snack Time!", 70, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to shoot", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to start", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Load all game graphics
background = pygame.image.load(path.join(img_path, "background.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_path, "pointing.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
mouth_img = pygame.image.load(path.join(img_path, "mouth.png"))
snack_images = []
snack_list = ['candy.png', 'candy2.png', 'cookie.png', 'cake.png', 'pudding.png', 'oreo.png', 'chocolate.png']
for img in snack_list:
    snack_image = pygame.image.load(path.join(img_path, img)).convert()
    snack_image = pygame.transform.scale(snack_image, (50, 50))
    snack_images.append(snack_image)
germ_images = []
germ_list = ['germ1.png', 'germ2.png']
for img in germ_list:
    germ_images.append(pygame.image.load(path.join(img_path, img)).convert())
explosion_anim = {}
explosion_anim['a'] = []
explosion_anim['b'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'hit.png'.format(i)
    img = pygame.image.load(path.join(img_path, filename)).convert()
    img.set_colorkey(BLACK)
    img_a = pygame.transform.scale(img, (50, 50))
    explosion_anim['a'].append(img_a)
    img_b = pygame.transform.scale(img, (30, 30))
    explosion_anim['b'].append(img_b)
    filename = 'hit.png'.format(i)
    img = pygame.image.load(path.join(img_path, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['medicine'] = pygame.image.load(path.join(img_path, 'medicine.png')).convert()
powerup_images['capsules'] = pygame.image.load(path.join(img_path, 'capsules.png')).convert()

shoot_sound = pygame.mixer.Sound(path.join(snd_path, 'shoot.mp3'))
power_sound = pygame.mixer.Sound(path.join(snd_path, 'recover.mp3'))
eating_sound = pygame.mixer.Sound(path.join(snd_path, 'eating.mp3'))
expl_sound = pygame.mixer.Sound(path.join(snd_path, 'beep.mp3'))
player_die_sound = pygame.mixer.Sound(path.join(snd_path, 'end.mp3'))
win_sound = pygame.mixer.Sound(path.join(snd_path, 'youwin.mp3'))
pygame.mixer.music.load(path.join(snd_path, 'Poupis_Theme.mp3'))
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(loops=-1)

game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        germs = pygame.sprite.Group()
        snacks = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        mouth = Mouth()
        all_sprites.add(player)
        all_sprites.add(mouth)
        for i in range(6):
            newgerm()
        score = 0

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    hits = pygame.sprite.groupcollide(germs, snacks, True, True)
    for hit in hits:
        score -= 30
        expl_sound.play()
        expl = Explosion(hit.rect.center, 'a')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newgerm()

    hits = pygame.sprite.spritecollide(player, germs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'b')
        all_sprites.add(expl)
        newgerm()
        if player.shield <= 0:
            expl_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'medicine':
            player.shield += random.randrange(10, 30)
            power_sound.play()
            player.lives += 1
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'capsules':
            player.powerup()
            power_sound.play()
            player.lives += 1
            if player.shield >= 100:
                player.shield = 100

    hits = pygame.sprite.spritecollide(mouth, snacks, True)
    for hit in hits:
        eating_sound.play()
        score += 50

    if player.lives == 0 and not death_explosion.alive():
        player_die_sound.play()
        game_over = True

    if score >= 1000:
        win_sound.play()
        game_over = True
    
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 150, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()

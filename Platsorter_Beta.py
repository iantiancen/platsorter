import pygame
from pygame.locals import *
import math
import sys
import numpy
 
pygame.init()
vec = pygame.math.Vector2
 
HEIGHT = 540
WIDTH = 960
ACC = 0.4
FRIC = -0.2
FPS = 60
DASH = 100

ROOMLENGTH = 4000 # must be a value larger than the width
 
FramePerSec = pygame.time.Clock()

win = False

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platsorter")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 

        # creates player sprite
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((69,69,69))
        self.rect = self.surf.get_rect()

        # defines and sets initial movement for player
        self.pos = vec((50, HEIGHT - 100))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.changepos = vec(0,0)
        self.projpos = vec(0,0)
        self.jumping = False
        self.doublejump = False
        self.walljump = False
        self.xdirection = 0

    def move(self):
        # gravity
        self.acc = vec(0,0.5)
    
        # check for left/right movement
        pressed_keys = pygame.key.get_pressed()            
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC      
        
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.changepos = self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.projpos = self.pos
            while True:
                if abs(self.changepos.y) < abs(self.changepos.x):
                    self.pos.y -= self.changepos.y/abs(self.changepos.x)
                    self.rect.midbottom = self.pos
                    if not pygame.sprite.spritecollide(self, platforms, False):
                        if self.changepos.y >= 0:
                            self.applyfriction(hits)
                        else:
                            self.vel.y = 0
                        break
                    self.pos.x -= numpy.sign(self.changepos.x)
                    self.rect.midbottom = self.pos
                    if not pygame.sprite.spritecollide(self, platforms, False):
                        self.wall()
                        break
                elif abs(self.changepos.y) > abs(self.changepos.x):
                    self.pos.y -= numpy.sign(self.changepos.y)
                    self.rect.midbottom = self.pos
                    if not pygame.sprite.spritecollide(self, platforms, False):
                        if self.changepos.y >= 0:
                            self.applyfriction(hits)
                        else:
                            self.vel.y = 0
                        break
                    self.pos.x -= self.changepos.x/abs(self.changepos.y)
                    self.rect.midbottom = self.pos
                    if not pygame.sprite.spritecollide(self, platforms, False):
                        self.wall()
                        break
                else:
                    break
        else:
            self.canjump = False

        self.pos.x += 1
        self.rect.midbottom = self.pos
        if pygame.sprite.spritecollide(self, platforms, False):
            self.walljump = True
            self.pos.x -= 1
            self.rect.midbottom = self.pos
        else:
            self.pos.x -= 2
            self.rect.midbottom = self.pos
            if pygame.sprite.spritecollide(self, platforms, False):
                self.walljump = True
                self.pos.x += 1
                self.rect.midbottom = self.pos
            else:
                self.walljump = False
                self.pos.x += 1
                self.rect.midbottom = self.pos

        if self.rect.right > WIDTH:
            self.pos.x = WIDTH - 30
        if self.rect.left < 0:
            self.pos.x = 30

    def ground(self):
        self.doublejump = True
        self.canjump = True
        '''
        self.candash = True
        '''

    def wall(self):
        self.walljump = True
        self.xdirection = numpy.sign(self.vel.x)
        self.vel.x = 0
        self.pos.y += 0.5
        self.vel.y = 0


    def applyfriction(self, hits):
        # undo movement
        self.vel.x -= self.acc.x
        self.pos = self.projpos

        # apply friction
        self.acc.x += self.vel.x * FRIC

        # redo movement
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.changepos = self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
                while True:
                    if abs(self.changepos.y) < abs(self.changepos.x):
                        self.pos.y -= self.changepos.y/abs(self.changepos.x)
                        self.rect.midbottom = self.pos
                        if not pygame.sprite.spritecollide(self, platforms, False):
                            if self.changepos.y >= 0:
                                self.ground()
                            self.vel.y = 0
                            break
                        self.pos.x -= numpy.sign(self.changepos.x)
                        self.rect.midbottom = self.pos
                        if not pygame.sprite.spritecollide(self, platforms, False):
                            self.wall()
                            break
                    elif abs(self.changepos.y) > abs(self.changepos.x):
                        self.pos.y -= numpy.sign(self.changepos.y)
                        self.rect.midbottom = self.pos
                        if not pygame.sprite.spritecollide(self, platforms, False):
                            if self.changepos.y >= 0:
                                self.ground()
                            self.vel.y = 0
                            break
                        self.pos.x -= self.changepos.x/abs(self.changepos.y)
                        self.rect.midbottom = self.pos
                        if not pygame.sprite.spritecollide(self, platforms, False):
                            self.wall()
                            break
                    else:
                        break

    def tryjump(self):
        if self.canjump == True and not self.jumping:
            self.jump()
        elif self.walljump == True:
            self.jumping = True
            self.vel.x = -numpy.sign(self.xdirection) * 5
            self.vel.y = -9
            self.walljump == False
        elif self.doublejump == True and not self.jumping:
            self.jump()
            self.doublejump = False
    
        
    def jump(self):
        self.jumping = True
        self.vel.y = -9
        self.conserve_x_vel()
    
    def cancel_jump(self):
        self.jumping = False
        if self.vel.y < -2:
            self.vel.y = -2

    def conserve_x_vel(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.vel.x = -abs(self.vel.x)
        if pressed_keys[K_RIGHT]:
            self.vel.x = abs(self.vel.x)

    '''
    def dash(self):
        if self.candash == True:
            pressed_keys = pygame.key.get_pressed()
            self.candash = False
            if pressed_keys[K_LEFT] and pressed_keys[K_UP]:
                self.pos.x -= DASH
                self.pos.y -= DASH
                self.vel.y = 0
                self.conserve_x_vel()
            elif pressed_keys[K_UP] and pressed_keys[K_RIGHT]:
                self.pos.x += DASH
                self.pos.y -= DASH
                self.vel.y = 0
                self.conserve_x_vel()                
            elif pressed_keys[K_RIGHT] and pressed_keys[K_DOWN]:
                self.pos.x += DASH
                self.pos.y += DASH
                self.vel.y = 0
                self.conserve_x_vel()
            elif pressed_keys[K_DOWN] and pressed_keys[K_LEFT]:
                self.pos.x -= DASH
                self.pos.y += DASH
                self.vel.y = 0
                self.conserve_x_vel()
            elif pressed_keys[K_UP]:
                self.pos.y -= DASH
                self.vel.y = 0      
            elif pressed_keys[K_DOWN]:
                self.pos.y += DASH
                self.vel.y = 0      
            elif pressed_keys[K_LEFT]:
                self.pos.x -= DASH
                self.conserve_x_vel()
            else:
                self.pos.x += DASH
                self.conserve_x_vel()
    '''
 
class Floor(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 30))
        self.surf.fill((0,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, y))

class Wall(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.surf = pygame.Surface((30, HEIGHT))
        self.surf.fill((0,0,0))
        self.rect = self.surf.get_rect(center = (x, HEIGHT/2))

class Platform(pygame.sprite.Sprite):
    def __init__(self, platnumber):
        super().__init__()
        self.surf = pygame.Surface((100, platnumber * 22))
        self.surf.fill((0,0,0))
        self.rect = self.surf.get_rect(left = 200 * platnumber, bottom = HEIGHT - 20)

class Winbox(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((40,40))
        self.surf.fill((0,255,0))
        self.rect = self.surf.get_rect(center = (ROOMLENGTH - 35, 45))
        self.level = 0
    def update(self):
        if self.rect.colliderect(P1.rect):
            self.level += 1

P1 = Player()
Ground = Floor(HEIGHT - 10)
Ceiling = Floor(10)
Leftwall = Wall(10)
Rightwall = Wall(ROOMLENGTH)
Level = Winbox()

all_sprites = pygame.sprite.Group()
all_sprites.add(Ground)
all_sprites.add(Ceiling)
all_sprites.add(Leftwall)
all_sprites.add(Rightwall)
all_sprites.add(Level)
all_sprites.add(P1)
 
platforms = pygame.sprite.Group()
platforms.add(Ground)
platforms.add(Ceiling)
platforms.add(Leftwall)
platforms.add(Rightwall)

borders = pygame.sprite.Group()
borders.add(Ground)
borders.add(Ceiling)

PT = [Platform(i) for i in range(20)]
for plat in PT:
    all_sprites.add(plat)
    platforms.add(plat)

while True:
    P1.move()
    Level.update()
    for event in pygame.event.get():	
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYUP:    
            if event.key == pygame.K_c:
                P1.cancel_jump() 
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_c:
                P1.tryjump()

            if event.key == pygame.K_r:
                P1.pos = vec(500, HEIGHT - 100)
                P1.vel.y = 0

            '''
            if event.key == pygame.K_x:
                P1.dash()
            '''
    if P1.pos.x >= WIDTH - 250 and Rightwall.rect.right - abs(P1.vel.x) >= WIDTH +10 and P1.vel.x > 0:
        while True:
            P1.pos.x -= 1
            Level.rect.x -= 1
            for plat in platforms:
                if plat not in borders:
                    plat.rect.x -= 1
            if not (P1.pos.x >= WIDTH - 250 and Rightwall.rect.right - abs(P1.vel.x) >= WIDTH +10 and P1.vel.x > 0):
                break

    elif P1.pos.x <= 250 and Leftwall.rect.left + abs(P1.vel.x) <= -1 and P1.vel.x < 0:
        while True:
            P1.pos.x += 1
            Level.rect.x += 1
            for plat in platforms:
                if plat not in borders:
                    plat.rect.x += 1
            if not (P1.pos.x <= 250 and Leftwall.rect.left + abs(P1.vel.x) <= -1 and P1.vel.x < 0):
                break

        
    P1.rect.midbottom = P1.pos
    displaysurface.fill((255,255,255))

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    if Level.level == 1:
        win = True
        for entity in all_sprites:
            entity.kill()
        font = pygame.font.SysFont('Arial', 128)
        text = font.render('You Win!', True, (0,0,0))
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2)

    if win:
        displaysurface.blit(text, textRect)

    pygame.display.update()
    FramePerSec.tick(FPS)
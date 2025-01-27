import pygame
from pygame.locals import *
import random
import sys
import numpy
import webbrowser

#initialise pygame and enable vector math
pygame.init()
vec = pygame.math.Vector2
 
#define some constants. Changing these will allow for a different experience.
HEIGHT = 540
WIDTH = 960
ACC = 0.4
FRIC = -0.2
FPS = 60
DASH = 100

ROOMLENGTH = 4000 #must be a value larger than the width
 
FramePerSec = pygame.time.Clock()

#creates the window
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platsorter")

#All code for the player character within this class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 

        # creates player sprite
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((69,69,69))
        self.rect = self.surf.get_rect()

        # defines and sets initial movement for player, as well as initialises some player variables used in calculations
        self.pos = vec((50, HEIGHT - 100))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.changepos = vec(0,0)
        self.projpos = vec(0,0)
        self.firstpos = vec(0,0)
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

        #moves the player according to velocity and accleration values and sets some variables accordingly
        self.vel += self.acc
        self.firstpos = self.pos
        self.pos += self.vel + 0.5 * self.acc
        self.changepos = self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

        #collision detection. This line checks if the player is colliding with any platform sprites.
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            #set a variable to the projected position the player was moved to earlier
            self.projpos = self.pos
            while True:
                #this code traces the player back along the line from the projected position back to the original position by calculating the gradient of the player's movement and moving the player back until a collision is no longer detected.
                #Depending on whether the last moveback was along the x or y axis, the game knows whether the collision was against a wall or against the ceiling/ground.
                #this is important for enabling friction, wallslides and walljumps.
                #this type of collision detection is also needed over simply checking the direction of the player's movement because it identifies where the collision occurs and also accounts for high velocity movement.
                # this first section is for if the player is moving faster in the y axis than x axis
                if abs(self.changepos.y) < abs(self.changepos.x): 
                    #move the player back a fraction of 1, based off the gradient of the player's motion
                    self.pos.y -= self.changepos.y/abs(self.changepos.x) 
                    self.rect.midbottom = self.pos
                    #collision check
                    if not pygame.sprite.spritecollide(self, platforms, False): 
                        #if no longer colliding, redo all x movment as usual, this is to prevent the player movement being locked when against the ground or wall.
                        self.pos.x = self.firstpos.x 
                        self.pos.x += self.changepos.x
                        self.rect.midbottom = self.pos

                        #check if there's a second collision after redoing x movement
                        if pygame.sprite.spritecollide(self, platforms, False): 
                            while True:
                                #if so, move back in the x direction until no longer colliding.
                                self.pos.x -= numpy.sign(self.changepos.x) 
                                self.rect.midbottom = self.pos
                                if not pygame.sprite.spritecollide(self, platforms, False):
                                    break
                            #stops x velocity after a collision in the x axis.
                            self.vel.x = 0 
                        #if the player does not hit a wall in the x axis, check if the player is on ground. If on ground, then reset jumps and apply friction.
                        else: 
                            self.pos.y += 1
                            self.rect.midbottom = self.pos
                            if pygame.sprite.spritecollide(self, platforms, False):
                                self.applyfriction()
                                self.ground() 
                            self.pos.y -= 1 
                        #this line sets the y velocity to 0 after a collision in the y axis.
                        self.vel.y = 0 
                        self.rect.midbottom = self.pos
                        break
                    #assuming the player is still in a collision after moving a bit back in the y direction, this moves the player back by 1 pixel in the x direction.
                    self.pos.x -= numpy.sign(self.changepos.x) 
                    self.rect.midbottom = self.pos
                    #once again, check for collisions, reapply y movement, check for collision again, and stop y movement if there is a collision.
                    if not pygame.sprite.spritecollide(self, platforms, False): 
                        self.pos.y = self.firstpos.y
                        self.pos.y += self.changepos.y
                        self.rect.midbottom = self.pos
                        if pygame.sprite.spritecollide(self, platforms, False):
                            while True:
                                self.pos.y -= numpy.sign(self.changepos.y)
                                self.rect.midbottom = self.pos
                                if not pygame.sprite.spritecollide(self, platforms, False):
                                    break
                        #since this is a collision in the x axis, enable wall sliding and wall jumps.
                        self.wall()
                        break
                #this chunk of code is the same as the above, however runs when the player is moving faster in the x axis than the y axis.
                elif abs(self.changepos.y) > abs(self.changepos.x): 
                    self.pos.y -= numpy.sign(self.changepos.y)
                    self.rect.midbottom = self.pos
                    if not pygame.sprite.spritecollide(self, platforms, False):
                        self.pos.x = self.firstpos.x
                        self.pos.x += self.changepos.x
                        self.rect.midbottom = self.pos
                        if pygame.sprite.spritecollide(self, platforms, False):
                            while True:
                                self.pos.x -= numpy.sign(self.changepos.x)
                                self.rect.midbottom = self.pos
                                if not pygame.sprite.spritecollide(self, platforms, False):
                                    break
                            self.vel.x = 0
                        else:
                            self.pos.y += 1
                            self.rect.midbottom = self.pos
                            if pygame.sprite.spritecollide(self, platforms, False):
                                self.applyfriction()
                                self.ground()
                            self.pos.y -= 1
                        self.vel.y = 0
                        self.rect.midbottom = self.pos
                        break
                    self.pos.x -= self.changepos.x/abs(self.changepos.y)
                    self.rect.midbottom = self.pos
                    if not pygame.sprite.spritecollide(self, platforms, False):
                        self.pos.y = self.firstpos.y
                        self.pos.y += self.changepos.y 
                        self.rect.midbottom = self.pos                       
                        if pygame.sprite.spritecollide(self, platforms, False):
                            while True:
                                self.pos.y -= numpy.sign(self.changepos.y)
                                self.rect.midbottom = self.pos
                                if not pygame.sprite.spritecollide(self, platforms, False):
                                    break
                        self.wall()
                        break
                else:
                    break
        else:
            #disables jumping when not on the ground
            self.canjump = False


        #checks if the player is 1 pixel away from a wall, if they are, enable wall jumping. This is so the player can walljump when near a wall and not just moving into it.
        self.pos.y += 1
        self.rect.midbottom = self.pos
        if not pygame.sprite.spritecollide(self, platforms, False):
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
        self.pos.y -= 1
        self.rect.midbottom = self.pos

        #in case the player goes off the left or right of the screen (might happen if the player moves fast enough to move past the side walls in a single frame) reset the player next to the edge wall
        #it's really difficult to get enough speed to actually pass through the walls however so this code is mostly redundant.
        if self.rect.right > WIDTH:
            self.pos.x = WIDTH - 30
        if self.rect.left < 0:
            self.pos.x = 30

    #refreshes normal jump and double jump, disables double jump, called when player touches any ground.
    def ground(self):
        self.doublejump = True
        self.canjump = True
        self.walljump = False

    #enables wall jumping if the player is moving into a wall, as well as slides the player down the wall at a constant velocity. xdirection tells the jumping code whether the player is on a left or right wall.
    def wall(self):
        self.walljump = True
        self.xdirection = numpy.sign(self.vel.x)
        self.vel.x = 0
        self.vel.y = 0.1

    #reduces x velocity only if the player is on ground. This enables skilled players to exploit the lack of friction in the air to gain lots of momentum.
    def applyfriction(self):
        # undo movement
        if self.vel.x != 0:
            self.vel.x -= self.acc.x
        self.pos.x = self.firstpos.x

        # apply friction
        self.acc.x += self.vel.x * FRIC

        # redo movement
        self.vel.x += self.acc.x
        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.changepos.x = self.vel.x + 0.5 * self.acc.x
        self.rect.midbottom = self.pos

    #checks whether the player can jump normally, wall jump or use a double jump, then performs the jump accordingly.
    def tryjump(self):
        #if the player is on the ground, jump normally
        if self.canjump == True and not self.jumping:
            self.jump()
        #if the player is next to a wall, perform a wall jump
        elif self.walljump == True:
            self.jumping = True
            self.vel.x = -numpy.sign(self.xdirection) * 5
            self.vel.y = -9
            self.walljump == False
        #if the player is in mid air, and the double jump has not been used, perform a double jump
        elif self.doublejump == True and not self.jumping:
            self.jump()
            self.doublejump = False
    
    #jump code
    #jumps are designed to keep the player's x momentum, allowing for the direction of x velocity to be changed.
    #this allows skilled players to perform advanced movement techniques to retain and increase x velocity to beat levels faster.
    def jump(self):
        self.jumping = True
        self.vel.y = -9
        self.conserve_x_vel()
    
    #code which reduces the height of any given jump. Triggered when the player releases the jump button.
    def cancel_jump(self):
        self.jumping = False
        if self.vel.y < -2:
            self.vel.y = -2

    #the function used to conserve x velocity. Can be used in future code modifications if additional functionality is added and requires x velocity to be retained.
    def conserve_x_vel(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.vel.x = -abs(self.vel.x)
        if pressed_keys[K_RIGHT]:
            self.vel.x = abs(self.vel.x)

#Class defining the floor and ceiling objects.
class Floor(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 30))
        self.surf.fill((0,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, y))

#class defining the boundary walls.
class Wall(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.surf = pygame.Surface((30, HEIGHT))
        self.surf.fill((0,0,0))
        self.rect = self.surf.get_rect(center = (x, HEIGHT/2))

#Class defining the platforms which get sorted. Numerous variables are passed in to allow for different heights and positions.
class Platform(pygame.sprite.Sprite):
    def __init__(self, platnumber):
        super().__init__()
        self.surf = pygame.Surface((100, (platnumber + 1) * 22))
        self.surf.fill((0,0,0))
        self.rect = self.surf.get_rect(left = 200 * (platnumber + 1), bottom = HEIGHT - 20)

#class for the text which appears in the top left at the start of every level.
class Text(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.SysFont('Cascadia Code', 64)
        self.surf = self.font.render('Level 1 - Selection Sort', True, (0,0,0))
        self.rect = self.surf.get_rect()
        self.rect.left = 45
        self.rect.top = 40

#class for the green box which advances the player to the next level.
class Winbox(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((40,40))
        self.surf.fill((0,255,0))
        self.rect = self.surf.get_rect(center = (ROOMLENGTH - 35, 45))
        self.level = 0
        self.time = 0
    def update(self):
        #check if the player is touching the box
        if self.rect.colliderect(P1.rect):
            #if the player is, move onto the next level
            self.level += 1
            #delete all the platforms, regardless of how sorted they are
            for plat in PT:
                plat.kill()
            #move the room back to the start
            while Leftwall.rect.left < -5:
                Level.rect.x += 1
                leveltext.rect.x += 1
                for plat in platforms:
                    if plat not in borders:
                        plat.rect.x += 1
            #reset the player's position, acceleration and velocity
            P1.pos = vec((50, HEIGHT - 100))
            P1.vel = vec(0,0)
            P1.acc = vec(0,0)
            P1.rect.midbottom = P1.pos
            #regenerate the platforms
            for i in range(len(PT)):
                PT[i] = Platform(i)
            for plat in PT:
                all_sprites.add(plat)
                platforms.add(plat)
            #randomise the platform order
            random.shuffle(PT)
            for i in range(len(PT)):
                PT[i].rect.left = 200 * (i+1)
            #reset the sorting variables so it starts from a fresh sort
            sort.__init__()
            #change the level text accordingly
            if self.level == 2:
                leveltext.surf = leveltext.font.render('Level 2 - Insertion Sort', True, (0,0,0))
                #insertion sort requires i to start at 1, so in this case i is set to 1.
                #without this, the sort.__init__() function would set i to 0.
                sort.i = 1
            elif self.level == 3:
                leveltext.surf = leveltext.font.render('Level 3 - Bubble Sort', True, (0,0,0))
            elif self.level == 4:
                leveltext.surf = leveltext.font.render('Level 4 - Bogo Sort', True, (0,0,0))

#class for buttons in the menus
class Button():
    def __init__(self, x, y, text, colour):
        self.font = pygame.font.SysFont('Cascadia Code', 64)
        self.surf = self.font.render(text, True, colour)
        self.text = text
        self.rect = self.surf.get_rect()
        self.rect.midbottom = (x, y)
        self.clicked = False

    def update(self):
        #action is a boolean which is returned. Code elsewhere allows for different buttons to have seperate functions. Action is returned as true if the button is clicked.
        action = False
        pos = pygame.mouse.get_pos()

        #if the cursor is hovering over the button, change the button colour
        if self.rect.collidepoint(pos):
            self.surf = self.font.render(self.text, True, (69,69,69))
            #if the button is clicked, return action as true. Clicked is set to true to prevent the button from being triggered multiple times from one click.
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        #sets the button colour back to black if the cursor is not hovering over it
        else:
            self.surf = self.font.render(self.text, True, (0,0,0))

        #when left click is released, set clicked to false to allow the button to be clicked multiple times.
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action

#class for text not designed to have any function
class Titletext():
    def __init__(self, x, y, text):
        self.font = pygame.font.SysFont('Cascadia Code', 128)  
        self.surf = self.font.render(text, True, (0, 0, 0))  
        self.rect = self.surf.get_rect()
        self.rect.midbottom = (x, y)

#creates all the objects (excluding the platforms to be sorted)
P1 = Player()
Ground = Floor(HEIGHT - 10)
Ceiling = Floor(10)
Leftwall = Wall(10)
Rightwall = Wall(ROOMLENGTH)
Level = Winbox()
leveltext = Text()
start_button = Button(480, 400, 'Start', (0,0,0))
help_button = Button(480, 470, 'How To Play', (0,0,0))
back_button = Button(480, 400, 'Back to Menu', (0,0,0))
title = Titletext(480, 120, 'Platsorter')
end = Titletext(480, 120, 'You Win!')

#adds all the sprites relevant to the game to the all sprites group
all_sprites = pygame.sprite.Group()
all_sprites.add(Ground)
all_sprites.add(Ceiling)
all_sprites.add(Leftwall)
all_sprites.add(Rightwall)
all_sprites.add(Level)
all_sprites.add(leveltext)
all_sprites.add(P1)

#adds all sprites the player needs to collide with into the platforms group
platforms = pygame.sprite.Group()
platforms.add(Ground)
platforms.add(Ceiling)
platforms.add(Leftwall)
platforms.add(Rightwall)

#group to prevent the ground and ceiling from scrolling to the side
borders = pygame.sprite.Group()
borders.add(Ground)
borders.add(Ceiling)

#creates a list of 19 platforms, each with different height values based on position in the list
PT = [Platform(i) for i in range(19)]
#adds the platforms to all sprites and platforms
for plat in PT:
    all_sprites.add(plat)
    platforms.add(plat)
    
#scrambles the order of the platforms
random.shuffle(PT)

#distribute the platforms across the level according to their position in the list
for i in range(len(PT)):
    PT[i].rect.left = 200 * (i+1)

#class to contain sorting algorithms    
class Sorting():
    #initialises variables required when sorting
    def __init__(self):
        self.i = 0
        self.j = 1
        self.k = 0
        self.min = 0
        self.key = 0
        self.sorting = True
        self.swapped = False
        self.stopsort = False
        self.inloop = False
        self.targeti = 0
        self.targetj = 0

    #function designed to change the heights of 2 platforms in positions i and j, to the target i and target j.
    def move(self):
        #if finished moving, toggle sorting to true to resume the sort algorithm
        if PT[self.i].rect.height == self.targeti:
            self.sorting = True
        else:
            if self.targeti > self.targetj:
                PT[self.i].surf = pygame.transform.scale(PT[self.i].surf, (PT[self.i].rect.width, PT[self.i].rect.height + 1))
                PT[self.i].rect.height += 1
                PT[self.j].surf = pygame.transform.scale(PT[self.j].surf, (PT[self.j].rect.width, PT[self.j].rect.height - 1))
                PT[self.j].rect.height -= 1
            else:
                PT[self.i].surf = pygame.transform.scale(PT[self.i].surf, (PT[self.i].rect.width, PT[self.i].rect.height - 1))
                PT[self.i].rect.height -= 1
                PT[self.j].surf = pygame.transform.scale(PT[self.j].surf, (PT[self.j].rect.width, PT[self.j].rect.height + 1))
                PT[self.j].rect.height += 1
            PT[self.i].rect.bottom = HEIGHT - 20
            PT[self.j].rect.bottom = HEIGHT - 20

    #sorting algorithm based off random swaps
    def bogo(self):
        if self.sorting == True:

            #check if the list is sorted. If it is, do not attempt to sort.
            for i in range(len(PT) - 1):
                if PT[i].rect.height < PT[i+1].rect.height:
                    self.stopsort = True
                else:
                    self.stopsort = False
                    break

            #if list is not sorted, swap two random values
            if self.stopsort == False:
                self.i = random.randint(0, len(PT) - 1)
                self.j = random.randint(0, len(PT) - 1)
                self.targeti = PT[self.j].rect.height
                self.targetj = PT[self.i].rect.height
                self.sorting = False
        self.move()

    #bubble sort algorithm, modified to work with the game loop and movement time.
    def bubble(self):
        if self.stopsort == False:
            #if not moving, find next swap
            if self.sorting == True: 
                if self.k != len(PT):
                    #iterate through unsorted part of the list
                    if self.i != len(PT) - self.k - 1:
                        #if adjacent heights are out of order, swap them
                        if PT[self.i].rect.height > PT[self.j].rect.height:
                            self.targeti = PT[self.j].rect.height
                            self.targetj = PT[self.i].rect.height    
                            self.sorting = False 
                            self.swapped = True
                    else:      
                        #if no swaps occured, list is sorted. flag is flipped to stop sorting. 
                        if self.swapped == False:
                            self.stopsort = True
                        self.swapped = False
                        #resets i and j and increases k for next iteration
                        self.i = -1
                        self.j = 0
                        self.k += 1 
            if self.sorting == False:
                self.move()
            #increments i and j each iteration if not moving.
            #this is essentially a modified for loop which runs through the game loop rather than on its own
            if self.sorting == True:
                self.i += 1
                self.j = self.i + 1

    #insertion sort algorithm. Modified to use its own move algorithm, also requires i to be set to 1.
    def insertion(self):
        if self.stopsort == False:
            if self.sorting == True: 
                # iterate from 1 to length of PT
                if self.i < len(PT):
                    #insertion sort has 2 types of swaps, the first, done here, shifts the entire list to make room for an insertion
                    if self.inloop == False:
                        self.key = PT[self.i].rect.height
                        self.k = self.i - 1
                        self.j = self.k + 1
                    if self.k >= 0 and self.key < PT[self.k].rect.height:
                        self.inloop = True
                        self.targetj = PT[self.k].rect.height
                        self.sorting = False
                    #second swap inserts the selected height in the correct place in the sorted section of the list
                    else:
                        self.inloop = False
                        self.targetj = self.key
                        self.sorting = False
                        self.i += 1
            #modified move algorithm, only changes one platform at a time
            if self.sorting == False:
                if PT[self.j].rect.height == self.targetj:
                    self.sorting = True
                else:
                    if PT[self.j].rect.height > self.targetj:
                        PT[self.j].surf = pygame.transform.scale(PT[self.j].surf, (PT[self.j].rect.width, PT[self.j].rect.height - 1))
                        PT[self.j].rect.height -= 1
                    else:
                        PT[self.j].surf = pygame.transform.scale(PT[self.j].surf, (PT[self.j].rect.width, PT[self.j].rect.height + 1))
                        PT[self.j].rect.height += 1
                    PT[self.j].rect.bottom = HEIGHT - 20
            if self.sorting == True:
                if self.inloop == True:
                    self.k -= 1
                    self.j = self.k + 1              

    #selection sort algorithm
    def selection(self):
        if self.stopsort == False:
            if self.sorting == True:
                # Iterate through list
                if self.i < len(PT):
                    # Find the smalled height in unsorted section
                    self.min = self.i
                    for j in range(self.i+1, len(PT)):
                        if PT[j].rect.height < PT[self.min].rect.height:
                            self.min = j
                    # swap said height with the height of the platform in the next position of the sorted part of the list
                    self.j = self.min       
                    self.targeti = PT[self.j].rect.height
                    self.targetj = PT[self.i].rect.height  
                    self.sorting = False
                else:
                    self.stopsort = True
            if self.sorting == False:
                    self.move()
            if self.sorting == True:
                self.i += 1

#create sort object, with all the sorting functions defined in the class
sort = Sorting()

#start of game loop
while True:
    #check for events (keypresses or exit)
    for event in pygame.event.get():
        #if quit, quit	
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        #if not in menu screen or victory screen, allow player to jump and reset player position
        if Level.level != 0 and Level.level != 5:
            #checks for when the c key is pressed
            if event.type == pygame.KEYUP:    
                if event.key == pygame.K_c:
                    P1.cancel_jump() 
            #checks when the c key is released. This allows the height of any jump to be varied.
            if event.type == pygame.KEYDOWN:    
                if event.key == pygame.K_c:
                    P1.tryjump()
                #reset key, in case the player does clip through a boundary and goes offscreen. Used more often in testing, not needeed in final game however is useful in case of undiscovered bugs causing the player to clip out of bounds.
                if event.key == pygame.K_r:
                    P1.pos = vec(500, HEIGHT - 100)
                    P1.vel.y = 0

    #menu screen code, appears when game launches, checks for button presses and displays the menu screen elements
    if Level.level == 0:  
        #button to start the game 
        if start_button.update() == True:
            leveltext.surf = leveltext.font.render('Level 1 - Selection Sort', True, (0,0,0))
            Level.level = 1
        #opens a link to a user manual
        if help_button.update() == True:
            webbrowser.open('https://drive.google.com/file/d/11A0TkZYnF2OSqexSpYlP_384eftp0jeC/view?usp=sharing')

        #code to render in the white background, followed by the 3 elements on top.
        displaysurface.fill((255, 255, 255))
        displaysurface.blit(start_button.surf, start_button.rect)
        displaysurface.blit(help_button.surf, help_button.rect)
        displaysurface.blit(title.surf, title.rect)

    #victory screen, similar to menu screen
    elif Level.level == 5:
        if back_button.update() == True:
            Level.level = 0
        displaysurface.fill((255, 255, 255))
        displaysurface.blit(end.surf, end.rect)
        displaysurface.blit(back_button.surf, back_button.rect)

    #main game code to run when not in menu screens
    else:
        #run a sorting algorithm depending on the level
        if Level.level == 1:
            sort.selection()
        elif Level.level == 2:
            sort.insertion()
        elif Level.level == 3:
            sort.bubble()
        elif Level.level == 4:
            sort.bogo()

        #move the player
        P1.move()

        #check if the player is touching the green box
        Level.update()
                
        #if the player tries to move past an invisible barrier to the right, stop the player movment and scroll the screen left.
        #screen only scrolls left as long as the rightwall stays at the boundary of the playing area.
        #this means the level stops scrolling when the player gets near the sides of the level.
        if P1.pos.x >= WIDTH - 250 and Rightwall.rect.right - abs(P1.vel.x) >= WIDTH +10 and P1.vel.x > 0:
            #while loop moves the player back and everything else back by 1 until the player is no longer past the scroll trigger barrier thing.
            while True:
                P1.pos.x -= 1
                Level.rect.x -= 1
                leveltext.rect.x -= 1
                for plat in platforms:
                    #doesn't move ground and ceiling
                    if plat not in borders:
                        plat.rect.x -= 1
                #break while loop after scrolling is complete
                if not (P1.pos.x >= WIDTH - 250 and Rightwall.rect.right - abs(P1.vel.x) >= WIDTH +10 and P1.vel.x > 0):
                    break
        
        #same side scrolling code but for moving left instead of right
        elif P1.pos.x <= 250 and Leftwall.rect.left + abs(P1.vel.x) <= -1 and P1.vel.x < 0:
            while True:
                P1.pos.x += 1
                Level.rect.x += 1
                leveltext.rect.x += 1
                for plat in platforms:
                    if plat not in borders:
                        plat.rect.x += 1
                if not (P1.pos.x <= 250 and Leftwall.rect.left + abs(P1.vel.x) <= -1 and P1.vel.x < 0):
                    break
        
        #sets the player rectangle location to the player pos variable
        P1.rect.midbottom = P1.pos

        #fill the background with white, covering everything drawn the previous frame
        displaysurface.fill((255,255,255))

        #draw all sprites in the all_sprites group on top
        for entity in all_sprites:
            displaysurface.blit(entity.surf, entity.rect)

    #update the display
    pygame.display.update()
    FramePerSec.tick(FPS)
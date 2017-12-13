#! /usr/bin/env python
# -*- coding:utf-8 -*-

# DiSCLAIMER : 
# Music free of royalties taken at :
# https://freesound.org/people/FoolBoyMedia/sounds/237089/

import pygame
import sys
import json
import re
from random import randint
from save_game_server import Server
 
# Global constants
 
SOUND = True

# Colors
BLACK = (0, 0, 0)
GREY = (50,50,50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 20, 147)
YELLOW = (255,255,0)
PURPLE = (148,0,211)
ORANGE = (255,132,0)
BROWN = (180, 115, 40)
 
# Screen dimensions

SCREEN_WIDTH = int(800*1.2)
SCREEN_HEIGHT = int(600*1.2)


NPLAYERS = 2

GRAVITY = 0.4
BULLET_SPEED = 10
PLAYER_SPEED = 6
INVINCIBILITY_TIME=1500

UNIT = 10



RESET_KEY = pygame.K_r
EXIT_KEY = pygame.K_ESCAPE



                #Width, height, top left x, top left y.
DEFAULT_LVL =   [
                  [200, UNIT, 120, 190],
                  [200, UNIT, 120, 440],
                  [2*UNIT, 200, 470, 40],
                  [2*UNIT, 200, 470, 400],
                  [200, UNIT, 640, 190],
                  [200, UNIT, 640, 440]
                ]

DEFAULT_SPAWNPOINTS = [(200, 160), (820, 160), (200, 400), (820, 400)]

 
#Event codes
LEFT = 'l'
RIGHT = 'r'
LEFT_KUP = 'm'
RIGHT_KUP = 'n'

JUMP = 'j'
SHOOT = 's'
RESET = 'x'


class SoundLibrary(object):
    """docstring for SoundLibrary"""
    def __init__(self):
        self.sounds = []


    def load_sounds(self):
        pygame.mixer.music.load('./sound_fx/bg_music.wav')
        pygame.mixer.music.play(-1)

        G1 = pygame.mixer.Sound('./sound_fx/grunt1.ogg')
        G2 = pygame.mixer.Sound('./sound_fx/grunt2.ogg')
        G2.set_volume(0.6)
        G3 = pygame.mixer.Sound('./sound_fx/grunt3.ogg')
        NOO = pygame.mixer.Sound('./sound_fx/nooo.ogg')
        NOO.set_volume(0.3)
        PEW = pygame.mixer.Sound('./sound_fx/pew.ogg')

        PREPARE = [pygame.mixer.Sound('./sound_fx/prepare.ogg'), pygame.mixer.Sound('./sound_fx/prepare2.ogg'), pygame.mixer.Sound('./sound_fx/prepare3.ogg')]
        WINNER = pygame.mixer.Sound('./sound_fx/winner.ogg')

        self.sounds =  [G1,                 #0
                        G2,                 #1
                        G3,                 #2
                        NOO,                #3
                        PEW,                #4
                        PREPARE[0],         #5
                        PREPARE[1],         #6
                        PREPARE[2],         #7
                        WINNER              #8
                        ]
    def play(self, i, s=True):
        if s == True and SOUND == True :
            self.sounds[i].play()
        

class Player(pygame.sprite.Sprite):

    def __init__(self, pname, pcol, nb, sprite=False, cit = ''):

        super(Player, self).__init__()
 
        self.name = pname
        self.cit = cit
        self.col = pcol

        self.lives = 3
        self.score = 0

        self.kb = []
        self.pnumber = nb
        self.last_death = 0

        # Create an image of the block, and fill it with a color.
        width = UNIT
        height = 2*UNIT
        if sprite == False:
            self.image = pygame.Surface([width, height])
            self.image.fill(self.col)
        else :
            self.image = pygame.image.load(sprite)

        self.sprite_save = self.image
 
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
 
        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0
 
        # List of sprites we can bump against
        self.level = None

        # Double jump is used 
        self.doublejump = False

        #last side looked
        self.look = 1
        self.im_look = 1

        self.bullets = []


    def set_kb(self, keybinds):
        self.kb = keybinds


    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        for b in self.bullets:
            b.update()
            if b.rect.left >= SCREEN_WIDTH or b.rect.right <= 0 or len(pygame.sprite.spritecollide(b, self.level.platform_list, False))>0:
                self.bullets.remove(b)
    
        # Move left/right
        self.rect.x += self.change_x
        

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
 
        # Move up/down
        self.rect.y += self.change_y
 
        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
 
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.doublejump = False
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
 
            # Stop our vertical movement
            self.change_y = 0

        t = pygame.time.get_ticks()-self.last_death
        if t < INVINCIBILITY_TIME :
            if t < 100 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            elif t < 200:
                self.image = self.sprite_save
                self.im_look = 1
            elif t < 300 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            elif t < 400:
                self.image = self.sprite_save
                self.im_look = 1
            elif t < 500 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            elif t < 600:
                self.image = self.sprite_save
                self.im_look = 1
            elif t < 700 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            elif t < 900:
                self.image = self.sprite_save
                self.im_look = 1
            elif t < 1000 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            elif t < 1100:
                self.image = self.sprite_save
                self.im_look = 1
            elif t < 1200 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            elif t < 1300:
                self.image = self.sprite_save
                self.im_look = 1
            elif t < 1400 : 
                self.image = pygame.Surface([UNIT, 2*UNIT])
                self.image.fill(BLACK)
            else:
                self.image = self.sprite_save
                self.im_look = 1

        if self.look != self.im_look:
            self.image = pygame.transform.flip(self.image,True,False)
            self.im_look = self.look



        #if self.rect.top >= SCREEN_HEIGHT :
         #   self.die()
 
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += GRAVITY
 
 
    def jump(self):
        """ Called when user hits 'jump' button. """
 
        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down
        # 1 when working with a platform moving down.
        playsound = False

        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
 
        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.doublejump == False: 
            self.change_y = -10
            self.doublejump = True
            playsound = True

        if len(platform_hit_list) > 0 : 
            self.doublejump = False

        return playsound

    def die(self, spawn):
        self.lives -= 1
        if self.lives >= 0 :
            self.rect.x = spawn[0]
            self.rect.y = spawn[1]
            self.change_x = 0
            self.change_y = 0
            self.last_death = pygame.time.get_ticks()

    def shoot(self):
        if len(self.bullets) <=2:
            self.bullets.append(Bullet(self))
            #play the sound
            return True
        return False
 

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -PLAYER_SPEED
        self.look = -1
 
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = PLAYER_SPEED
        self.look = +1
 
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0

class Bullet(pygame.sprite.Sprite):
    """Bullets"""
    def __init__(self, player):
        super(Bullet, self).__init__()
        self.image = pygame.Surface([UNIT/2, UNIT/2])
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.left-UNIT/2 if player.look < 0 else player.rect.right+UNIT/2
        self.rect.y = player.rect.y
        self.dir = player.look

    def update(self):
        self.rect.x += BULLET_SPEED*self.dir

    def draw(self, screen):
        pygame.draw.rect(screen,WHITE,self.rect)


        

 
class Platform(pygame.sprite.Sprite):
    """ Platform the player can jump on """
 
    def __init__(self, width, height):
        super(Platform, self).__init__()
 
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
 
        self.rect = self.image.get_rect()
 
 
class Level(object):
 
    def __init__(self, player, lvl):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """

        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player
         
        # Background image
        self.background = None

        level = lvl 
 
        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
 

    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
 
    def draw(self, screen):
        """ Draw everything on this level. """
 
        # Draw the background
        if self.background == None :
            screen.fill(BLACK)
        else:
            screen.blit(pygame.transform.scale(self.background,(SCREEN_WIDTH,SCREEN_HEIGHT)), (0,0))
 
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)


def draw_bullets(screen, players):
    for p in players :
        for b in p.bullets :
            b.draw(screen)

def bullet_hit(players, spawns):
    for i in range(len(players)):
        others = pygame.sprite.Group()
        for j in range(len(players)):
            if j == i : 
                j += 1
            else :
                for b in players[i].bullets:    
                    if pygame.sprite.collide_rect(b, players[j]) == True and (pygame.time.get_ticks()-players[j].last_death)>INVINCIBILITY_TIME:
                        players[j].die(spawns[randint(0,len(spawns)-1)])
                        players[i].score += 50
                        players[i].bullets.remove(b)
        i += 1


def print_score(screen, myfont, players, crown):
    i = 0
    scores = []
    for p in players :
        textname = myfont.render(p.name, False, p.col)
        screen.blit(textname, (UNIT+i*150 +i*3*UNIT +4*UNIT, UNIT))
        
        textlives = myfont.render("Lives : "+str(p.lives), False, WHITE)
        screen.blit(textlives, (UNIT+i*150 +i*3*UNIT +4*UNIT, 4*UNIT))
        
        textscore = myfont.render("Score : "+str(p.score), False, WHITE)
        screen.blit(textscore, (UNIT+i*150 +i*3*UNIT +4*UNIT, 7*UNIT))
        screen.blit(pygame.transform.scale(p.sprite_save, (2*UNIT, 4*UNIT)), (UNIT+i*150+i*3*UNIT, 2*UNIT))

        scores.append(p.score)
        i += 1
    if max(scores) > 0:    
        winning = scores.index(max(scores))
        screen.blit(pygame.transform.scale(crown, (int(1.5*UNIT),int(1.5*UNIT))), (int(0.4*UNIT)+winning*150+winning*3*UNIT, int(1.1*UNIT)) )



def print_pnames(screen, myfont, players):
    #Put player names above their head
    for p in players :
        textname = myfont.render(p.name, False, p.col)
        textrect = textname.get_rect()
        screen.blit(textname, (p.rect.x-textrect.width/2, p.rect.y-2*UNIT))

def rematch(players, level, spawns, active_sprite_list):
    #rematch setup
    for p in players :
        p.level = level
        spawn = spawns[randint(0,len(spawns)-1)]
        p.rect.x = spawn[0]
        p.rect.y = spawn[1]
        p.lives = 3
        p.bullets = []
        p.image = p.sprite_save
        p.im_look = 1
        active_sprite_list.add(p)

def give_nplayers(final_screen, size):
    #Choose number of players at startup
    screen = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
    n=0
    arn = pygame.image.load('./img/Larene.png')
    clock = pygame.time.Clock()
    width = 3
    padding = 2

    font = pygame.font.SysFont('liberationsans', 2*UNIT)
    font.set_bold(True)
    pos = [0,1,2]
    nplay = [2,3,4]
    i = 0
    while n < 2 or n > 4:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    i -= 1
                if event.key == pygame.K_RIGHT:
                    i += 1
                if event.key == pygame.K_RETURN:
                    n = nplay[i]

                if event.key == EXIT_KEY:
                    sys.exit()
            if event.type == pygame.QUIT :
                sys.exit()

        if i < 0 : i = 2
        if i > 2 : i= 0

        screen.fill(BLACK)
        screen.blit(pygame.transform.scale(arn, (SCREEN_HEIGHT, int(0.323*SCREEN_HEIGHT))), ((SCREEN_WIDTH-SCREEN_HEIGHT)/2, UNIT*4))
        for j in range(3):
            if j == i :
                textname = font.render(str(j+2)+" Players", False, YELLOW)
                textrect = textname.get_rect()
                a_rect = pygame.Surface((textrect.width+2*(width+padding),textrect.height+2*(width+padding)))
                a_rect.fill(YELLOW)
                block_rect = pygame.Surface((textrect.width+2*padding, textrect.height+2*padding))
                block_rect.fill(BLACK)

                screen.blit(a_rect, ((j+1)*SCREEN_WIDTH/4-textrect.width/2-(width+padding), SCREEN_HEIGHT/2-(width+padding)))
                screen.blit(block_rect, ((j+1)*SCREEN_WIDTH/4-textrect.width/2-padding, SCREEN_HEIGHT/2-padding))


            else:
                textname = font.render(str(j+2)+" Players", False, WHITE)
                textrect = textname.get_rect()

            screen.blit(textname, ((j+1)*SCREEN_WIDTH/4-textrect.width/2, SCREEN_HEIGHT/2))

        final_screen.blit(pygame.transform.scale(screen, size), (0,0))
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(60)
 
        # Update the screen
        pygame.display.flip()
    return n


def menu(S, final_screen, size, all_characters, nplayers, all_kb):
    screen = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    totalp = len(all_characters)

    width = 3
    padding = 2
    dist_from_top = int(0.323*SCREEN_HEIGHT) +10*UNIT
    startleft = SCREEN_WIDTH/2-(totalp/2)*4*UNIT
    flushleft = 10*UNIT
    arn = pygame.image.load('./img/Larene.png')


    font = pygame.font.SysFont('liberationsans', 2*UNIT)
    font.set_bold(True)

    chosen = {}
    i = 0
    while len(chosen)<nplayers :
        screen.fill(BLACK)
        screen.blit(pygame.transform.scale(arn, (SCREEN_HEIGHT, int(0.323*SCREEN_HEIGHT))), ((SCREEN_WIDTH-SCREEN_HEIGHT)/2, UNIT*4))

        c = len(chosen)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == all_kb[c][1]:
                    i -= 1
                if event.key == all_kb[c][2]:
                    i += 1
                if event.key == all_kb[c][3]:
                    if i not in chosen.values():
                        chosen[c]=i
                    
                if event.key == EXIT_KEY:
                    sys.exit()
            if event.type == pygame.QUIT :
                sys.exit()


        if i < 0 : i = totalp-1
        if i >= totalp : i = 0
        
        for j in range(totalp) :
            second_row = 0
            jp = j

            if j >= totalp/2:
                second_row = 8*UNIT
                jp -= totalp/2

            col = all_characters[j].col
            textname = font.render(all_characters[j].name, False, col)
            textrect = textname.get_rect()
            imsurf = pygame.Surface([6*UNIT, 6*UNIT])

            imsurf.blit(pygame.transform.scale(all_characters[j].sprite_save, [3*UNIT, 6*UNIT]), (int(1.5*UNIT),0))
            imrect = imsurf.get_rect()
            textcit = font.render('"'+all_characters[j].cit+'"', False, col)
            citrect = textcit.get_rect()
            if j == i :

                a_rect = pygame.Surface((imrect.width+2*(width+padding),imrect.height+2*(width+padding)))
                a_rect.fill(col)
                block_rect = pygame.Surface((imrect.width+2*padding, imrect.height+2*padding))
                block_rect.fill(BLACK)

                screen.blit(a_rect, (startleft+jp*8*UNIT-(width+padding), dist_from_top-(width+padding)+second_row))
                screen.blit(block_rect, (startleft+jp*8*UNIT-padding, dist_from_top-padding + second_row))


                screen.blit(textname, (SCREEN_WIDTH/2-textrect.width/2,  dist_from_top-4*UNIT))
                screen.blit(textcit, (SCREEN_WIDTH/2-citrect.width/2,  dist_from_top+18*UNIT))

            screen.blit(imsurf, (startleft+8*UNIT*jp, dist_from_top + second_row))

            if j in chosen.values():
                textplay = font.render("P"+str(1+chosen.values().index(j)), False, col)
                darken = pygame.Surface([6*UNIT, 6*UNIT])
                darken.fill(BLACK)
                darken.set_alpha(180)

                screen.blit(darken, (startleft+8*UNIT*jp, dist_from_top + second_row))
                screen.blit(pygame.transform.scale(textplay, [6*UNIT, 6*UNIT]), (startleft+8*UNIT*jp, dist_from_top + second_row))




        final_screen.blit(pygame.transform.scale(screen, size), (0,0))
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(60)
 
        # Update the screen 
        pygame.display.flip()

    return chosen



def load_levels(filename):

    levels = []
    spawns = []
    with open(filename, 'r') as f:
      lines = f.read().splitlines()

    i=0
    for i in range(len(lines)) :  
      if lines[i] == 'LVL':
        levels.append(json.loads(lines[i+1]))

      if lines[i]== 'SPAWNPOINTS':
        spawns.append(json.loads(lines[i+1]))

    if len(spawns) == len(levels):
        return levels, spawns
    else:
        print "ERROR : Problem with "+filename+", Are the levels and spawns defined correclty ?\n"
        sys.exit()

def load_keybinds(filename):
    keybinds = []

    with open(filename, 'r') as f:
      lines = f.read().splitlines()

    i=0
    pat = re.compile("^P\d$")
    for i in range(len(lines)) :  
      if pat.match(lines[i]) :
        kb = []
        for j in range(1,5):
          kb.append(getattr(pygame, 'K_'+ lines[i+j].split(':')[1]))
        keybinds.append(kb)
    return keybinds


def inits():
    #pygame inits
    if SOUND == True:
        pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    pygame.font.init()
    
    if SOUND == True:
        pygame.mixer.init()
    return SoundLibrary()

def load_characters():
    #Create characters
    char1 = Player('Gwendal', RED, 0, sprite='./img/gwendal.png', cit="GwendaaaaaaAAAAAAaaaaal !!")
    char2 = Player(u'El Péhème', BLUE, 1, sprite='./img/elpeheme.png', cit=u"On va les éclater, et quand je dis on, c'est plutôt moi..." )
    char3 = Player('Huberr', GREEN, 1, sprite='./img/huberr.png', cit = u"Je pense qu'on sait pas trop encore qui va gagner")
    char4 = Player('Bastien', PINK, 2, sprite='./img/bastien.png', cit = u"GroOmpF !")
    char5 = Player('Mr.Punchline', YELLOW, 0, sprite='./img/mrpunchline.png', cit=u"L'ARENE est une aventure dont on ne sort pas vivant.")
    char6 = Player('Superdev', PURPLE, 1, sprite='./img/supdev.png', cit=u"You don't fuck with the Super Developper")
    char7 = Player(u"L'Abbé Dai", ORANGE, 0, sprite='./img/ACP.png', cit=u"L'Abbé Dai est ACPté.")
    char8 = Player("Blatteman", BROWN, 0, sprite='./img/blatteman.png', cit=u"Le seul VRAI habitant de la cave...")
    charNo = Player('NOPLAYER', WHITE, 0, sprite='./img/noplayer.png')

    return [char1, char2, char3, char4, char5, char6, char7, char8, charNo, charNo]


def get_events(player, key_evs, alive, match_done, done):
    events = ''
    for event in key_evs:
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN :
                if alive :
                    if match_done == False:
                        if event.key == player.kb[1]:
                            events += LEFT
                            
                        if event.key == player.kb[2]:
                            events += RIGHT

                        if event.key == player.kb[0]:
                            events += JUMP
                           
                        if event.key == player.kb[3]:
                            events += SHOOT
                
                if event.key == EXIT_KEY:
                    done = True 
                if event.key == RESET_KEY:
                    events += RESET
                    # reset = True
 
            if event.type == pygame.KEYUP:

                if event.key == player.kb[1]:
                    events += LEFT_KUP
                if event.key == player.kb[2]:
                    events += RIGHT_KUP
    return (events, done)














def main():
    """ Main Program """
#Pygame inits
    SL = inits()

#AUDIO
    if SOUND == True:
        SL.load_sounds()

#FONTS
    myfont = pygame.font.SysFont('liberationsans', 2*UNIT)
    winfont = pygame.font.SysFont('liberationsans', 6*UNIT)
    winfont.set_bold(True)
    mysmallfont = pygame.font.SysFont('liberationsans', int(1.5*UNIT))
    mysmallfont.set_bold(True)

#SCREEN

    #Get display size of monitor
    infoObject = pygame.display.Info()
    size = (int(infoObject.current_w), int(infoObject.current_h-80))

    final_screen = pygame.display.set_mode(size)#, pygame.FULLSCREEN)
    screen = pygame.Surface([SCREEN_WIDTH,SCREEN_HEIGHT])
 
    pygame.display.set_caption("L'ARENE")

    crown = pygame.image.load('./img/crown.png')


    # Create the characters

    all_players = load_characters()
    
    #Read the keybinds from keybinds.config
    all_kb = load_keybinds('keybinds.config')
    

    nplayers = give_nplayers(final_screen, size)


#RESEAU
    S = Server('', 12345,nplayers)
    S.start_server()




    #char select
    chosen = menu(S, final_screen, size, all_players, nplayers, all_kb)

    players = []

    for i in range(nplayers):
        players.append(all_players[chosen[i]])
        players[i].set_kb(all_kb[i])


    # Read levels and spawns from levels.config
    all_levels, all_spawns = load_levels('./levels.config')

    # Create all the levels
    level_list = []
    for l in all_levels :
            level_list.append(Level(players[0], lvl = l))

    current_level_no = randint(0,len(all_levels)-1)
    current_level = level_list[current_level_no]
    spawns = all_spawns[current_level_no]
 
    active_sprite_list = pygame.sprite.Group()

    #Sound
    SL.play(randint(5,7))

    for p in players :
        # Set the current level

        p.level = current_level
     
        spawn = spawns[randint(0,len(spawns)-1)]
        p.rect.x = spawn[0]
        p.rect.y = spawn[1]
        active_sprite_list.add(p)
     

 
    # Loop until user clicks close button or presses ESC
    done = False
    match_done = False
    win = 0
    reset = True
    win_play = False

    dead_players = []
    alive_players = range(nplayers)
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
 
    # -------- Main Program Loop -----------
    while not done:
        
        all_events = []
        key_events = S.events #pygame.event.get()
        S.events = ['']*nplayers

        #Get the events

        for i in range(nplayers):
            p = players[i]
            if i in alive_players:
                alive = True
            else : 
                alive = False
            events, done = get_events(p, key_events, alive, match_done, done)
            all_events.append(events)

        #Apply/Interpret the events

        for i in range(nplayers):
            p = players[i]

            for action in all_events[i] :
                if action == LEFT:
                    p.go_left()
                if action == RIGHT:
                    p.go_right()
                if action == JUMP:
                    s = p.jump()
                    SL.play(p.pnumber, s=s)
                    
                if action == SHOOT:
                    s = p.shoot()
                    SL.play(4, s=s)

                if action == RESET:
                    reset = True

                if action == LEFT_KUP and p.change_x < 0:
                    p.stop()
                if action == RIGHT_KUP and p.change_x > 0:
                    p.stop()

        # Update the players.
        active_sprite_list.update()
 
        # Update items in the level
        current_level.update()
 
        # Block players within the left-right boundaries of the world
        for p in [players[index] for index in alive_players]:

            if p.rect.right > SCREEN_WIDTH:
                p.rect.right = SCREEN_WIDTH
     
            if p.rect.left < 0:
                p.rect.left = 0
            
            #Kill players that drop below screen
            if p.rect.top >= SCREEN_HEIGHT :
                p.die(spawns[randint(0,len(spawns)-1)])
     
        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        draw_bullets(screen, [players[index] for index in alive_players])

        bullet_hit([players[index] for index in alive_players], spawns)

        print_score(screen, myfont, players, crown)
        print_pnames(screen, mysmallfont, [players[index] for index in alive_players])


        # Check if one is dead
        
        for i in alive_players:
            if players[i].lives <= 0:
                players[i].lives = 0
                players[i].kill()
                SL.play(3)
                dead_players.append(i)
                alive_players.remove(i)

        if len(alive_players) == 1:
            win = alive_players[0]


        if len(alive_players) <= 1 :
            if win_play == False:
                SL.play(8)
                win_play = True


            match_done = True
            textname = winfont.render(players[win].name+" WINS !", False, players[win].col)
            textrect = textname.get_rect()
            screen.blit(textname, (SCREEN_WIDTH/2-textrect.width/2, SCREEN_HEIGHT/2))
            
            players[win].kill()

        else :
            reset = False

        if reset == True:
            reset = False
            match_done = False
            win_play = False
            
            #SCORE
            players[win].score += 100 + players[win].lives*50
            win = 0
            alive_players = range(nplayers)
            dead_players = []

            #Change level
            current_level_no = randint(0,len(all_levels)-1)
            current_level = level_list[current_level_no]
            spawns = all_spawns[current_level_no]
            rematch(players, current_level, spawns, active_sprite_list)
            SL.play(randint(5,7))


        final_screen.blit(pygame.transform.scale(screen, size), (0,0))
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(60)
 
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
        



    pygame.quit()
 
if __name__ == "__main__":
    main()
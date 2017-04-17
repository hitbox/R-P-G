import logging
import os
import pygame
import pygame.gfxdraw
import random
import sys
import time

from pygame.locals import *

logging.basicConfig()
logger = logging.getLogger('rpg')
logger.setLevel(logging.DEBUG)

playG = True

mapno = 0
mapbool = True

GAME_OVER_SCREEN = False

START, INFO, EXIT = range(3)
buttons = [False] * 3

battle = False
make_random_enemy = True
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def bch(bcc):
    global BATTLE_CH
    BATTLE_CH = random.randint(bcc, 20)

bch(1)
current_enemy = random.randint(0,3)

info_text = ["This is a little project made with pygame, trying to be a Roguelike.",
             "Coded entirely by mynameajeff."]

TILE_WIDTH = 15
TILE_HEIGHT = 15

def parse_map(fn):
    global current_map
    current_map = []
    path = "level/%s.lvl" % (fn, )
    for line in open(path).readlines():
        for hero in line.split(" "):
            if hero in " \n":
                continue
            current_map.append(hero)

BLACK = (0,0,0)
WHITE = (255,255,255)

MAP_COLORS = {
    '1': (100,100,100),
    '2': (100,0,0),
    '3': (0,0,100),
    '4': (0,100,0),
    '5': (120,120,255),
    '-': BLACK,
}

def render_map(mapPosX, mapPosY, tch):
    x2 = 0
    y = 25
    for hero in current_map:
        if hero in "123456-":
            color = MAP_COLORS[hero]
            draw_color_rect(x2+mapPosX,y+mapPosY,TILE_WIDTH+tch,TILE_HEIGHT,color)
        elif hero == "+":
            # NextLine
            x2=-TILE_WIDTH
            y += TILE_HEIGHT
        x2 += tch + TILE_WIDTH

class Button:

    def __init__(self, text, x, y, width, height, inner_color, outer_color):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inner_color = inner_color
        self.outer_color = outer_color
        self.textsize = 40

    def draw(self, hover=False):
        inner_color = (self.outer_color if hover else self.inner_color, ) * 3
        outer_color = (self.inner_color if hover else self.outer_color, ) * 3

        size = 5

        draw_color_rect(self.x, self.y, self.width, self.height, inner_color)
        draw_color_rect(self.x+size, self.y+size, self.width-(size*2), self.height-(size*2), outer_color)

        img = render_text(self.text, "munro", self.textsize, (100,100,100))
        rect = img.get_rect()
        rect2 = pygame.Rect(0, 0, self.width, self.height)
        rect2.topleft = (self.x, self.y)
        rect.center = rect2.center
        screen.blit(img, rect)

    def collision(self, mousex, mousey, callback, *args):
        if (self.x + self.width > mousex > self.x and self.y + self.height > mousey > self.y):
            callback(*args)

class Item:

    def __init__(self):
        self.iWid = TILE_WIDTH #itemWid
        self.iHei = TILE_HEIGHT #itemHei
        self.it1 = 1
        self.it2 = 1
        self.d2 = []
        self.d = []

    def drawcall(self, iX2, iY2, typebl):
        iX = (15 * iX2) - 5
        iY = (15 * iY2) + 10

        if self.it2 == self.it1 and typebl == 1:
            draw_color_rect(iX,iY,self.iWid,self.iHei,(0,0,255))

        elif self.it2 == self.it1 and typebl == 2:
            draw_color_rect(iX,iY,self.iWid,self.iHei,(0,100,255))

        if hero.cX+(hero.size / 15) > iX2 >= hero.cX:
            if hero.cY+(hero.size/15) > iY2 >= hero.cY:
                if typebl == 1:
                    self.drawcallext1()
                else:
                    self.drawcallext2()
                self.it2 += 1

    def drawcallext1(self):
        hero.size += 15
        logger.debug("mcdonalds collected")

    def drawcallext2(self):
        if hero.hp >= (hero.hpmax-40):
            hero.hp = hero.hpmax
        else:
            hero.hp += 40
        logger.debug("health collected")

    def randomitem(self, items):
        for x in range(items):
            # n1 x 15 42
            self.d.append(random.randint(15,42))
            # n2 y 1 30
            self.d.append(random.randint(1,30))
            self.d.append(random.randint(1,2))
            self.d2.append(Item())

itemclass = Item()

def r(run):
    itemclass.randomitem(10)
    x3s = 0
    for x in range(run):
        itemclass.d2[x].drawcall(itemclass.d[x3s], itemclass.d[x3s+1], itemclass.d[x3s+2])
        x3s += 3

class Player:

    def __init__(self, color):
        self.hpmax = 100
        self.hp = 100
        self.size = 15
        self.level = 1 #current level
        self.level_up = 25 #xp for next level
        self.xp = 0 #experience points
        self.dmgM = 1 #damage multiplier
        self.color = color

        self.cX = 17
        self.cY = 6

    def Calc(self):
        while self.xp >= self.level_up:
            logger.debug("Level Up!")
            self.level += 1
            self.xp -= self.level_up
            self.level_up = round(self.level_up * 1.5)
            self.hp = round(self.hp * 1.75)
            self.hpmax = round(self.hpmax * 1.75)
            self.dmgM *= 2

    def draw_hp(self, hpX, hpY, enemi):
        xrloop = 0
        draw_color_rect(hpX, hpY, 75, 10, (255,0,0))
        draw_color_text(str(self.hp - enemi.totalDmgDealt), hpX + 79, hpY - 2, "freesans", 11, BLACK)
        for x in range(int(self.hp-enemi.totalDmgDealt)):
            draw_color_rect(hpX + xrloop, hpY, 75 / self.hpmax, 10, (0,255,0))
            xrloop += 75 / self.hpmax

    def HPch(self, enemi):
        global GAME_OVER_SCREEN
        self.hp -= enemi.totalDmgDealt

        if self.xp < 0:
            hero.xp = 0

        if self.hp < 1:
            time.sleep(0.1)
            GAME_OVER_SCREEN = True

        return self.hp

    def drawcall(self):
        cX = (15 * self.cX)-5
        cY = (15 * self.cY)+10
        draw_color_rect(cX, cY, self.size, self.size, self.color)

hero = Player((120,240,68))

class Enemy:

    totalDmgTaken = 0 #to the enemy
    totalDmgDealt = 0

    description = ""

    def __init__(self, **kwargs):
        for name in ['strength', 'xpout', 'gearband', 'lutband', 'color',
                     'textMov', 'HPmax', 'width']:
            setattr(self, name, kwargs.get(name, getattr(self, name)))

        self.x = 250
        self.y = 180

    def info(self, name):
        # 250,180
        draw_color_rect(self.x, self.y, 80, 195, self.color)
        draw_color_text(name, 265-self.textMov, 140, "munro", 20, (200,200,200))

    def draw_hp(self):
        # The enemy's health bar.
        xrloop = 0
        draw_color_rect(self.x-1,self.y-20,81,10,(255,0,0))
        draw_color_text(str(self.HPmax-self.totalDmgTaken),self.x+84,self.y-22,"freesans",11,BLACK)
        for x in range(self.HPmax-self.totalDmgTaken):
            draw_color_rect(self.x+xrloop,self.y-20,80/self.HPmax,10,(0,255,0))
            xrloop+=80/self.HPmax

    def HPch(self, enemy_name, enemi):
        global battle,make_random_enemy
        # hpcurrent - random number [0 to yourDamage(with chance of crit)]

        self.totalDmgTaken+= 100 * hero.dmgM

        if self.totalDmgTaken >= self.HPmax:
            draw_color_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK)
            hero.xp+= self.xpout
            hero.Calc()
            logger.debug("You Win! You killed the %s", enemy_name)
            make_random_enemy = True
            bch(1)
            parse_map("btl")
            hero.HPch(enemi)
            init_enemies()
            battle = False

    def run_away(self, enemy_name, enemi):
        global battle,make_random_enemy

        draw_color_rect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT,BLACK)
        logger.debug("you pussied out of the fight.")
        make_random_enemy = True
        bch(1)
        parse_map("btl")
        hero.HPch(enemi)
        init_enemies()
        battle = False

    def AI(self, enemy_name, enemi):
        global battle,make_random_enemy
        attack_power = random.randint(0, self.strength)

        if self.totalDmgTaken < self.HPmax:
            if attack_power == 0:
                logger.debug("The %s missed when attacking you!", enemy_name)
            else:
                self.totalDmgDealt +=(3*attack_power)
                logger.debug("The %s has attacked you for %s damage!", enemy_name, 3 * attack_power)

                if self.totalDmgDealt >= hero.hp:
                    draw_color_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK)
                    logger.debug("The %s has defeated you!", enemy_name)
                    make_random_enemy = True
                    bch(0)
                    parse_map("btl")
                    hero.HPch(enemi)
                    init_enemies()
                    battle = False


class Imp(Enemy):

    strength = 2
    xpout = 10
    gearband = "Destitute Gear"
    lutband = "Destitute Loot"
    color = (25,120,25)
    textMov = 0
    HPmax = 500
    width = 80
    description = "weak but can be strong in numbers."


class Orc(Enemy):

    strength = 5
    xpout = 25
    gearband = "Poor Gear"
    lutband = "Destitute Loot"
    color = (85,120,25)
    textMov = 0
    HPmax = 800
    width = 80
    description = "the imp's tougher brother."


class Gremlin(Enemy):

    strength = 8
    xpout = 35
    gearband = "Poor Gear"
    lutband = "Poor Loot"
    color = (45,120,55)
    textMov = 14
    HPmax = 1200
    width = 80
    description = "not as weak as you may think."


class Goblin(Enemy):

    strength = 12
    xpout = 22
    gearband = "Decent Gear"
    lutband = "Poor Loot"
    color = (65,120,65)
    textMov = 10
    HPmax = 1400
    width = 80
    description = "the toughest normal enemy in the first area."


def init_enemies():
    global enemies
    #Gremloblin = Enemy(15,64,"Hard Scales","Decent Loot",(125,120,125),25,3000,80)
    enemies = [Imp(), Orc(), Gremlin(), Goblin()]

def draw_color_rect(x, y, width, height, color):
    pygame.draw.rect(screen, color, (x,y,width,height))

def draw_color_ball(x, y, radius, color):
    pygame.gfxdraw.filled_circle(screen,x,y,radius-1,color)
    pygame.gfxdraw.aacircle(screen,x,y,radius-1,color)

def render_text(text, font, size, color, antialias=True):
    path = "fonts/%s.ttf" % (font, )
    font = pygame.font.Font(path, size)
    return font.render(text, antialias, color)

def draw_color_text(text, x, y, font, fsize, color):
    path = "fonts/%s.ttf" % (font, )
    myfont = pygame.font.Font(path, fsize)
    msg = myfont.render(text, 1, color)
    screen.blit(msg, (x,y))

enemies_names = ["an Imp","an Orc","a Gremlin","a Goblin"]

BATTLE_ATTACK, BATTLE_DEFEND, BATTLE_INFO, BATTLE_RUN = range(4)
boolist = [False] * 4 #bt0,bt1,bt2,bt3

def gameover():
    draw_color_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK)
    draw_color_text("GAME OVER",(SCREEN_WIDTH/2)-120,(SCREEN_HEIGHT/2)-40,"freesans",40,WHITE)

lmbtimer = 0
xoffset = 0

battle_buttons = [
    Button("Attack", 7, 25, 160, 50, 155, 135),
    Button("Defend", 7, 80, 160, 50, 155, 135),
    Button("Info", 7, 135, 160, 50, 155, 135),
    Button("Run", 7, 190, 160, 50, 155, 135)
]

def update_battle(mousex, mousey, lmb):
    global current_enemy,mapbool,boolist,lmbtimer,output

    def callback(c, boolist, tl, lmb):
        global lmbtimer
        #button.draw(40, tl[loop], tl[loop+4], 5, True, 135, 115)
        button.draw(True)
        if lmb and lmbtimer <= 0:
            lmbtimer += 0.2
            for cloop in range(4):
                if c == cloop:
                    boolist[cloop] = True

    tl = [30, 30, 52, 52, 28, 82, 138, 193]

    # creates gray bar at top of canvas
    draw_color_rect(0,0,SCREEN_WIDTH,20,(128,128,128))
    draw_main_space()
    # Contains buttons
    draw_color_rect(0,20,180,SCREEN_HEIGHT,(70,70,70))
    # Divider
    draw_color_rect(175,20,5,SCREEN_HEIGHT,(90,90,90))

    if mapno == 1 and not mapbool:
        parse_map("btl")
        init_enemies()
        mapbool = True

    render_map(175, 95, 5)

    draw_color_rect(SCREEN_WIDTH-180-xoffset, SCREEN_HEIGHT-180, 75, 75, hero.color)
    draw_color_text("Battle Mode!", SCREEN_WIDTH/2-18, 2, "freesans", 12, BLACK)

    for loop in range(len(enemies)):

        if current_enemy == loop:
            enemies[loop].info(enemies_names[loop])
            enemies[loop].draw_hp()
            hero.draw_hp(SCREEN_WIDTH-180, SCREEN_HEIGHT-200, enemies[loop])

        button = battle_buttons[loop]
        button.draw()
        button.collision(mousex, mousey, callback, loop, boolist, tl, lmb)

        if boolist[loop]:
            enem = enemies_names[loop]
            enemy = enemies[loop]
            if loop == BATTLE_ATTACK:
                logger.debug("you attacked %s for %s damage!", enem, (100 * hero.dmgM))
                enemy.HPch(enem, enemy)
                enemy.AI(enem, enemy)
            elif loop == BATTLE_DEFEND:
                logger.debug("to be coded!")
            elif loop == BATTLE_INFO:
                logger.debug("%s, %s" % (enem, enemy.description))
            elif loop == BATTLE_RUN:
                enemy.run_away(enem, enemy)

        boolist[loop] = False
        if lmbtimer > 0:
            lmbtimer-=0.01

def draw_main_space():
    # creates main draw space
    draw_color_rect(0,20,SCREEN_WIDTH,SCREEN_HEIGHT,(185,185,185))

def update_hero(charhp, charcsize, charlvl, charlvlN, charxp, chardmgM):
    global TILE_WIDTH,TILE_HEIGHT,playG,output

    # creates gray bar at top of canvas
    draw_color_rect(0,0,SCREEN_WIDTH,20,(128,128,128))
    draw_main_space()

    render_map(220, 0, 0)
    draw_color_rect(0,20,220,SCREEN_HEIGHT,(70,70,70))
    draw_color_rect(215,20,5,SCREEN_HEIGHT,(90,90,90))

    [("Health", charhp), ("Char Size", charcsize)]

    alist1 = ["Health", "Char Size", "Level", "Next", "XP", "DMG*",
              charhp, charcsize, charlvl, charlvlN, charxp, chardmgM]
    avar1 = 50
    for x in range(6):
        s = alist1[x] + ": " + str(alist1[x+6])
        draw_color_text(s, 20, avar1, "munro", 30, (100,100,100))
        avar1+=30
    r(10)
    hero.drawcall()

main_screen_buttons = {
    'info_back': Button("<==",20,25,SCREEN_WIDTH/5,50,255,235),
    'start': Button("Start", SCREEN_WIDTH/3, SCREEN_HEIGHT/2, SCREEN_WIDTH/3, 50, 255, 235),
    'info': Button("Info", SCREEN_WIDTH/3, SCREEN_HEIGHT/1.5, SCREEN_WIDTH/3, 50, 255, 235),
    'exit': Button("Exit", SCREEN_WIDTH/3, SCREEN_HEIGHT/1.2, SCREEN_WIDTH/3, 50, 255, 235),
}

def update_info(mousex, mousey, lmb):

    def callback():
        button.draw(True)
        if lmb:
            buttons[INFO] = False

    draw_main_space()
    draw_color_text(info_text[0],20,80,"freesans", 18, (100,100,100))
    draw_color_text(info_text[1],22,110,"freesans", 18, (100,100,100))

    button = main_screen_buttons['info_back']
    button.draw()
    button.collision(mousex, mousey, callback)

def draw_title(mousex, mousey, lmb):

    def callback(button, lmb):
        button.draw(True)
        if lmb and button.text == "Exit":
            sys.exit()

    # creates gray bar at top of canvas
    draw_color_rect(0,0,SCREEN_WIDTH,20,(128,128,128))
    draw_main_space()
    draw_color_text("RPG", SCREEN_WIDTH/2-112, SCREEN_HEIGHT/6, "pxlvetica", 128, (100,100,100))

    names = ["Start", "Info", "Exit"]
    offsets = [60, 70, 70]
    divs = [2, 1.5, 1.2]

    for button in main_screen_buttons.values():
        button.draw()
        button.collision(mousex, mousey, callback, button, lmb)

def update(x, y, left):
    global mapno,mapbool,playG,make_random_enemy,current_enemy,battle

    if GAME_OVER_SCREEN:
        playG = True
        battle = False
        gameover()

    if BATTLE_CH == 0:
        if make_random_enemy:
            current_enemy = random.randint(0,3)
            make_random_enemy = False
            battle = True
        playG = True

    if not battle and buttons[START] and not GAME_OVER_SCREEN:
        mapno = 0
        update_hero(hero.hp, hero.size, hero.level, hero.level_up, hero.xp, hero.dmgM)

    if battle and buttons[START] and not GAME_OVER_SCREEN:
        mapno +=1
        playG = True #disables controls
        update_battle(x, y, left)
    else:
        playG = False

    if buttons[INFO]:
        update_info(x,y,left)

    if not buttons[START] and not buttons[INFO]:
        draw_title(x, y, left)

    if mapno == 0 and mapbool:
        parse_map("b")
        mapbool = False

def controls(event, x, y):
    csize2 = (hero.size / 15)

    if event.key == pygame.K_UP:
        logger.debug("Y; U: %s", hero.cY)
        if hero.cY <= 1:
            hero.cY = 1
        else:
            hero.cY -= 1

    elif event.key == pygame.K_DOWN:
        logger.debug("Y; D: %s", hero.cY)
        if hero.cY >= 31 - csize2:
            hero.cY = 31 - csize2
        else:
            hero.cY += 1

    elif event.key == pygame.K_LEFT:
        logger.debug("X; L: %s", hero.cX)
        if hero.cX <= 15:
            hero.cX = 15
        else:
            hero.cX -= 1

    elif event.key == pygame.K_RIGHT:
        logger.debug("X; R: %s", hero.cX)
        if hero.cX >= 43 - csize2:
            hero.cX = 43 - csize2
        else:
            hero.cX += 1

    hero.Calc()
    bch(0)

def main():
    screen.set_alpha(None)
    pygame.display.set_caption("RPG")
    clock = pygame.time.Clock()

    while not buttons[EXIT]:
        mousex, mousey = pygame.mouse.get_pos()
        lmb, _, _ = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                buttons[EXIT] = True
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == K_END:
                    buttons[EXIT] = True
                    sys.exit()

                elif not playG:
                    controls(event, mousex, mousey)

        update(mousex, mousey, lmb)
        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()

import os
import pygame
import random
import textwrap
import traceback

from collections import defaultdict

SWITCHSTATE = pygame.USEREVENT

FONTSIZE = 50
TEXTWRAPWIDTH = 20

SCREEN_SIZE = (768, 768)
TILE_SIZE = (64, 64)

def Surface(size):
    return pygame.Surface(size, pygame.SRCALPHA)

def rect_label(text, rect, color, background=None, border=None):
    font = Font()

    image = Surface(rect.size)

    if background is not None:
        image.fill(background)

    if border is not None:
        pygame.draw.rect(image, border, rect, 1)

    textimage = font.render(text, color)
    textrect = textimage.get_rect()
    textrect.center = rect.center

    image.blit(textimage, textrect)
    return image

def fitted(text, rect, background=None, **fontkwargs):
    fontsize = 1
    while True:
        font = Font(size=fontsize, **fontkwargs)
        size = font.size(text)
        if size > rect.size:
            image = Surface(rect.size)
            if background is not None:
                image.fill(background)
            rect = image.get_rect()

            textimage = font.render(text)
            textrect = textimage.get_rect()
            textrect.center = rect.center

            image.blit(textimage, textrect)
            return image
        fontsize += 1

class Font(object):

    def __init__(self, filename='PressStart2P', color=None, size=None):
        if color is None:
            color = (255,255,255)
        if size is None:
            size = FONTSIZE
        path = os.path.join('fonts', '%s.ttf' % (filename, ))
        self._font = pygame.font.Font(path, size)
        self.color = color

    def render(self, text, color=None):
        color = color or self.color
        renders = [ self._font.render(line, True, color) for line in text.splitlines() ]
        rects = [ image.get_rect() for image in renders ]

        # stack
        for r1, r2 in zip(rects[:-1], rects[1:]):
            r2.top = r1.bottom

        size = (max(rect.width for rect in rects),
                sum(rect.height for rect in rects))
        rv = Surface(size)

        for image, rect in zip(renders, rects):
            rv.blit(image, rect)

        return rv

    def size(self, text):
        return self._font.size(text)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()


class Entity(Sprite):

    def __init__(self, image, maxhealth, experience=0):
        super(Entity, self).__init__(image)
        self.health = self.maxhealth = maxhealth
        self.experience = experience


class Hero(Entity):

    def __init__(self):
        rect = pygame.Rect((0,0), TILE_SIZE)
        image = fitted('Hero', rect, background=(31,31,31), color=(201,111,16))
        super(Hero, self).__init__(image, 100)

class EnemyMeta(type):

    registry = defaultdict(list)

    def __new__(meta, name, bases, dict_):
        cls = super(EnemyMeta, meta).__new__(meta, name, bases, dict_)
        if name != 'Enemy':
            cls.registry[cls]
        return cls


class Enemy(Entity):

    __metaclass__ = EnemyMeta

    color = None
    maxhealth = None
    experience = None

    def __init__(self):
        name = self.__class__.__name__
        rect = pygame.Rect((0,0), TILE_SIZE)
        image = fitted(name, rect, background=(31,31,31), color=self.color)
        super(Enemy, self).__init__(image, self.maxhealth, self.experience)


class Imp(Enemy):

    color = (165,18,4)
    maxhealth = 10
    experience = 1


class Orc(Enemy):

    color = (72,147,53)
    maxhealth = 50
    experience = 10


class Gremlin(Enemy):

    color = (129,219,133)
    maxhealth = 50
    experience = 15


class Goblin(Enemy):

    color = (76,130,79)
    maxhealth = 75
    experience = 15


class Button(pygame.sprite.Sprite):

    def __init__(self, text, rect, on_click, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)

        self.images = dict(
            normal=rect_label(text, rect, (125,125,125), (31,31,31), (65,65,65)),
            hovering=rect_label(text, rect, (255,255,255), (31,31,31), (125,125,125)))

        self.image = self.images['normal']
        self.rect = self.image.get_rect()

        self.on_click_callback = on_click

    def exit_hover(self):
        self.image = self.images['normal']

    def on_click(self, event):
        print(self, event, self.on_click_callback)
        if callable(self.on_click_callback):
            self.on_click_callback(event)

    def on_hover(self):
        self.image = self.images['hovering']


class VerticalButtonGroup(pygame.sprite.OrderedUpdates):

    def __init__(self, labels_and_callbacks, pady=0):
        font = Font()
        labels = list(t[0] for t in labels_and_callbacks)
        callbacks = list(t[1] for t in labels_and_callbacks)
        sizes = list(map(font.size, labels))
        rect = pygame.Rect(0, 0, max(size[0] for size in sizes), max(size[1] for size in sizes))
        rect.width += 50
        rect.height += 25

        buttons = [ Button(text, rect, callback) for text, callback in zip(labels, callbacks) ]
        for b1, b2 in zip(buttons[:-1], buttons[1:]):
            b2.rect.top = b1.rect.bottom + pady

        pygame.sprite.OrderedUpdates.__init__(self, *buttons)

    def center(self, position):
        rect = pygame.Rect(min(button.rect.left for button in self),
                           min(button.rect.top for button in self),
                           max(button.rect.width for button in self),
                           sum(button.rect.height for button in self))
        rect2 = rect.copy()
        rect2.center = position

        dx, dy = rect2.x - rect.x, rect2.y - rect.y
        for button in self:
            button.rect.move_ip(dx, dy)


class BaseState(object):

    def draw(self, surface):
        pass

    def update(self):
        pass


class BaseMenuState(BaseState):

    def __init__(self):
        self.buttons = []
        self.hovering = None
        self.do_hover(pygame.mouse.get_pos())

    def do_hover(self, pos):
        for button in self.buttons:
            hit = button.rect.collidepoint(pos)
            if hit and self.hovering is None:
                button.on_hover()
                self.hovering = button
            elif hit and self.hovering is not button:
                self.hovering.exit_hover()
                self.hovering = button
                self.hovering.on_hover()
            elif not hit and self.hovering is button:
                self.hovering.exit_hover()
                self.hovering = None

    def mousemotion(self, event):
        self.do_hover(event.pos)

    def mousebuttondown(self, event):
        for button in self.buttons:
            hit = button.rect.collidepoint(event.pos)
            if hit and event.button == 1:
                button.on_click(event)


class MainMenuState(BaseMenuState):

    def __init__(self):
        super(MainMenuState, self).__init__()
        font = Font()
        _, rect = getscreen()

        self.title = Sprite(font.render('RPyG', (255,255,255)))
        self.title.rect.centerx = rect.centerx
        self.title.rect.top = rect.height / 4

        self.buttons = VerticalButtonGroup([('Start', self.switch_playstate),
                                            ('Info', self.switch_infostate),
                                            ('Exit', quit)],
                                           pady=10)
        self.buttons.center(rect.center)
        self.do_hover(pygame.mouse.get_pos())

    def draw(self, surface):
        surface.blit(self.title.image, self.title.rect)
        self.buttons.draw(surface)

    def keydown(self, event):
        if event.key in (pygame.K_q, pygame.K_ESCAPE):
            quit(event)

    def switch_infostate(self, event):
        switchstate(InfoState)

    def switch_playstate(self, event):
        switchstate(PlayState)


class InfoState(BaseMenuState):

    def __init__(self):
        super(InfoState, self).__init__()
        font = Font()

        _, rect = getscreen()

        s = '\n'.join(textwrap.wrap(
            'A super-awesome Roguelike!'
            ' With a text renderer that handles newlines!'
            ' Man this is a lot of text isn\'t it?',
            TEXTWRAPWIDTH))
        self.info = Sprite(font.render(s, (255,255,255)))
        self.info.rect.center = rect.center

        self.buttons = VerticalButtonGroup([ ('Back', self.switch_mainmenu) ])

    def switch_mainmenu(self, event):
        switchstate(MainMenuState)

    def draw(self, surface):
        surface.blit(self.info.image, self.info.rect)
        self.buttons.draw(surface)

    def keydown(self, event):
        self.switch_mainmenu(event)


class PlayingSharedState(object):

    _data = {}

    def __init__(self):
        self.__dict__ = self._data


class PlayState(PlayingSharedState):

    def __init__(self):
        super(PlayState, self).__init__()
        _, rect = getscreen()

        self.hero = Hero()
        self.hero.rect.topleft = map(lambda v: v * TILE_SIZE[0], (6, 6))

        self.enemies = [ random.choice(Enemy.registry.keys())() for _ in range(12) ]

        others = set([self.hero])
        for enemy in self.enemies:
            while True:
                pos = tuple(map(lambda v: v * TILE_SIZE[0], (random.randint(0, 12), random.randint(0, 12))))
                enemy.rect.topleft = pos
                if not any(enemy.rect.colliderect(other.rect) for other in others):
                    others.add(enemy)
                    break

        self.current = TravelState()
        self.fighting = None

    def draw(self, surface):
        self.current.draw(surface)

    def keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.switch_mainmenu(event)
        else:
            self.current.keydown(event)

    def mousebuttondown(self, event):
        self.switch_mainmenu(event)

    def switch_mainmenu(self, event):
        switchstate(MainMenuState)

    def update(self):
        self.current.update()
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.hero.rect):
                self.fighting = enemy
                switchstate(BattleState)
                break


class TravelState(PlayingSharedState):

    def __init__(self):
        super(TravelState, self).__init__()
        _, rect = getscreen()
        self.map = Surface(rect.size)
        self.map.fill((72, 147, 53))

    def draw(self, surface):
        surface.blit(self.map, (0,0))
        for enemy in self.enemies:
            surface.blit(enemy.image, enemy.rect)
        surface.blit(self.hero.image, self.hero.rect)

    def keydown(self, event):
        if event.key == pygame.K_DOWN:
            self.hero.rect.y += self.hero.rect.height
        elif event.key == pygame.K_UP:
            self.hero.rect.y -= self.hero.rect.height
        elif event.key == pygame.K_LEFT:
            self.hero.rect.x -= self.hero.rect.width
        elif event.key == pygame.K_RIGHT:
            self.hero.rect.x += self.hero.rect.width

    def update(self):
        pass


class BattleState(PlayingSharedState):

    def __init__(self):
        super(BattleState, self).__init__()
        print '%s battling %s' % (self.hero, self.fighting)

    def draw(self, surface):
        pass

    def update(self):
        pass


def getscreen():
    surface = pygame.display.get_surface()
    rect = surface.get_rect()
    return surface, rect

def main():
    SCREEN = pygame.Rect((0, 0), SCREEN_SIZE)
    FRAMERATE = 60

    screen = pygame.display.set_mode(SCREEN.size)
    screen_rect = screen.get_rect()
    clock = pygame.time.Clock()

    class DummyState(object):
        def draw(self, surface):
            pass
        def update(self):
            pass
    state = DummyState()

    EVENT_TYPES = [pygame.KEYDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                   pygame.MOUSEBUTTONUP]

    def gethandlers(state):
        handlers = {}
        for type_ in EVENT_TYPES:
            name = pygame.event.event_name(type_).lower()
            handler = getattr(state, name, None)
            if handler:
                handlers[type_] = handler
        return handlers

    handlers = {}
    next_event = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SWITCHSTATE:
                next_event = event

            if event.type in handlers:
                handlers[event.type](event)

        state.update()

        screen.fill((0,0,0))
        state.draw(screen)
        pygame.display.update()

        dt = clock.tick(FRAMERATE)

        if next_event is not None:
            state = next_event.state()
            # update event handlers
            handlers = gethandlers(state)
            next_event = None
            pygame.event.clear()


def switchstate(class_):
    return pygame.event.post(pygame.event.Event(SWITCHSTATE, state=class_))

def quit(event):
    pygame.event.post(pygame.event.Event(pygame.QUIT))

if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    pygame.event.post(pygame.event.Event(SWITCHSTATE, state=MainMenuState))
    main()

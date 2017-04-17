import os
import pygame

class Font(object):

    def __init__(self, filename='pxlvetica'):
        path = os.path.join('fonts', '%s.ttf' % (filename, ))
        self._font = pygame.font.Font(path, 50)

    def render(self, text, color):
        return self._font.render(text, True, color)

    def size(self, text):
        return self._font.size(text)


def rect_label(text, rect, color, background, border):
    font = Font()

    image = pygame.Surface(rect.size)
    image.fill(background)

    pygame.draw.rect(image, border, rect, 1)

    textimage = font.render(text, color)
    textrect = textimage.get_rect()
    textrect.center = rect.center

    image.blit(textimage, textrect)
    return image

class Button(pygame.sprite.Sprite):

    def __init__(self, text, rect, on_click, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)

        self.images = dict(
            normal=rect_label(text, rect, (125,125,125), (31,31,31), (65,65,65)),
            hovering=rect_label(text, rect, (255,255,255), (31,31,31), (125,125,125)))

        self.image = self.images['normal']
        self.rect = self.image.get_rect()

        self.on_click_callback = on_click

    def exit_hover(self, event):
        self.image = self.images['normal']

    def on_click(self, event):
        print(self, event, self.on_click_callback)
        if callable(self.on_click_callback):
            self.on_click_callback(event)

    def on_hover(self, event):
        self.image = self.images['hovering']


class VerticalButtonGroup(pygame.sprite.OrderedUpdates):

    def __init__(self, labels_and_callbacks):
        font = Font()
        labels = list(t[0] for t in labels_and_callbacks)
        callbacks = list(t[1] for t in labels_and_callbacks)
        sizes = list(map(font.size, labels))
        rect = pygame.Rect(0, 0, max(size[0] for size in sizes), max(size[1] for size in sizes))
        rect.width += 50
        rect.height += 25

        buttons = [ Button(text, rect, callback) for text, callback in zip(labels, callbacks) ]
        for b1, b2 in zip(buttons[:-1], buttons[1:]):
            b2.rect.top = b1.rect.bottom

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


def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    SCREEN = pygame.Rect(0, 0, 640, 480)
    FRAMERATE = 60

    screen = pygame.display.set_mode(SCREEN.size)
    screen_rect = screen.get_rect()
    clock = pygame.time.Clock()

    def quit(event):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    hovering = None
    buttons = VerticalButtonGroup([('Start', None), ('Info', None), ('Exit', quit)])
    buttons.center(screen_rect.center)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    quit(event)

            elif event.type == pygame.MOUSEMOTION:
                for button in buttons:
                    hit = button.rect.collidepoint(event.pos)
                    if hit and hovering is None:
                        button.on_hover(event)
                        hovering = button
                    elif hit and hovering is not button:
                        hovering.exit_hover(event)
                        hovering = button
                        hovering.on_hover(event)
                    elif not hit and hovering is button:
                        hovering.exit_hover(event)
                        hovering = None

            elif event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    hit = button.rect.collidepoint(event.pos)
                    if hit and event.button == 1:
                        button.on_click(event)

        screen.fill((0,0,0))
        buttons.draw(screen)
        pygame.display.update()

        dt = clock.tick(FRAMERATE)

if __name__ == '__main__':
    main()

import os

import pygame
import pygame.constants as const
from pygame.compat import geterror


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, const.RLEACCEL)
    return image, image.get_rect()


class Enterprise(pygame.sprite.Sprite):
    def __init__(self):
        super(). __init__()
        self.image, self.rect = load_image("ship_enterprise.png", WHITE)

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos


class Warbird(pygame.sprite.Sprite):
    def __init__(self):
        super(). __init__()
        self.image, self.rect = load_image("ship_warbird.png", WHITE)

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.right = self.area.right
        self.rect.top = 10
        self.move_y = 4

    def update(self):
        newpos = self.rect.move((0, self.move_y))
        if newpos.bottom > self.area.bottom or \
                newpos.top < self.area.top:
            self.move_y = -self.move_y
            newpos = self.rect.move((0, self.move_y))
        self.rect = newpos


class Torpedo(pygame.sprite.Sprite):
    def __init__ (self):
        super(). __init__()
        self.image, self.rect = load_image("federation_torpedo.png", BLACK)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed


class Score(pygame.sprite.Sprite):

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy
        self.font = pygame.font.Font(None, 50)
        # Our font color in rgb
        self.color = (255, 165, 0)
        self.score = 0  # start at zero
        self.render()

    def update(self):
        pass

    def add(self, points):
        """Adds the given number of points to the score."""
        self.score += points
        self.render()

    def render(self):
        """Updates the score. Renders a new image and re-centers at the initial coordinates."""
        self.image = self.font.render("Score: {}".format(self.score), True, self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.xy


class TheGame:

    def __init__(self):
        self.screen = None
        self.bg_image = None

        pygame.init()

    def init_display(self, display_width, display_height):
        mode = pygame.RESIZABLE
        size = (display_width, display_height)
        self.screen = pygame.display.set_mode(size, mode)

        self.bg_image, _ = load_image('background2.jpg')

        # Apply the background
        self.screen.blit(self.bg_image, (0, 0))

    def run(self):
        # initial display setup
        self.init_display(1200, 700)
        pygame.display.set_caption('STAR TREK WARS I')
        pygame.display.update()

        clock = pygame.time.Clock()
        enterprise = Enterprise()
        warbird = Warbird()
        score = Score((0, 0))
        allsprites = pygame.sprite.RenderUpdates((enterprise, warbird, score))
        torpedo_list = pygame.sprite.Group()

        # Main Loop
        going = True
        while going:
            # Do our events warrant a full display update
            full_update = False

            # clear previous draws to avoid trailing effect
            allsprites.clear(self.screen, self.bg_image)

            # limit loop to 60 frames per second
            clock.tick(60)

            # Handle Input Events
            for event in pygame.event.get():
                if event.type == const.QUIT:
                    going = False
                elif event.type == const.KEYDOWN and event.key == const.K_ESCAPE:
                    going = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    torpedo = Torpedo()
                    # Set the torpedo so it is where the player is
                    torpedo.rect.center = enterprise.rect.center
                    # Add the torpedo to the lists
                    allsprites.add(torpedo)
                    torpedo_list.add(torpedo)
                elif event.type == pygame.VIDEORESIZE:
                    self.init_display(event.w, event.h)
                    full_update = True
            allsprites.update()

            # Calculate mechanics for each torpedo
            for torpedo in pygame.sprite.spritecollide(warbird, torpedo_list, True):
                torpedo_list.remove(torpedo)
                allsprites.remove(torpedo)
                score.add(1)

            # Draw changes
            changes = allsprites.draw(self.screen)
            if full_update:
                pygame.display.update()
            else:
                pygame.display.update(changes)

        pygame.quit()


if __name__ == '__main__':
    TheGame().run()

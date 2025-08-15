import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from talk import *

from events import GLOBAL_EVENT

MAP_VIEW = False

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        pg.time.set_timer(GLOBAL_EVENT, 40)
        self.map_view = MAP_VIEW
        self.conversation = None
        self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        self.ai_talker = Talk()

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        if self.conversation:
            self.conversation.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f"{self.clock.get_fps() :.1f}")


    def draw(self):
        self.screen.fill("black")
        if not self.map_view:
            self.object_renderer.draw()
            self.weapon.draw()
        else:
            self.map.draw()
            self.player.draw()


    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
 
            elif event.type == GLOBAL_EVENT:
                self.global_trigger = True
#            self.player.single_fire_event(event)
            self.player.start_or_end_conversation(event)
            if self.conversation:
                self.conversation.handle_event(event)
 

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.check_events()
            self.update()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()

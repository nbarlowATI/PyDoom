import sys
import pygame as pg

from wad_data import WADData
from map_renderer import MapRenderer
from player import Player
from bsp import BSP
from seg_handler import SegHandler
from view_renderer import ViewRenderer

from doomsettings import *

class DoomEngine:
    def __init__(self, wad_path="wad/Doom1.wad"):
        self.wad_path = wad_path
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 1 / 60
        self.on_init()

    def on_init(self):
        self.wad_data = WADData(self, map_name="E1M1")
        self.map_renderer = MapRenderer(self)
        self.player = Player(self)
        self.bsp = BSP(self)
        self.seg_handler = SegHandler(self)
        self.view_renderer = ViewRenderer(self)

    def update(self):
        self.player.update()
        self.seg_handler.update()
        self.bsp.update()
        self.dt = self.clock.tick()
        pg.display.set_caption(f"{self.clock.get_fps()}")
        

    def draw(self):
        pg.display.flip()  # put flip here for debug draw
        self.screen.fill('black')
      #  self.map_renderer.draw()
#        pg.display.flip()

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False
                pg.quit()


    def run(self):
        while self.running:
            self.update()
            self.check_events()
            self.draw()
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    game = DoomEngine()
    game.run()
        
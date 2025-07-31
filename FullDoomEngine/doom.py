import sys
import pygame as pg

from wad_data import WADData
from map_renderer import MapRenderer
from player import Player
from bsp import BSP
from object_handler import ObjectHandler
from raycasting import RayCasting
from seg_handler import SegHandler
from sounds import SoundEffect
from view_renderer import ViewRenderer

from events import *
from doomsettings import *


class DoomEngine:
    def __init__(self, wad_path="wad/DOOM1.wad"):
        self.map_mode = False
        self.wad_path = wad_path
        self.screen = pg.display.set_mode(WIN_RES, pg.SCALED)
        self.framebuffer = pg.surfarray.array3d(self.screen)
        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 1 / 60
        self.on_init()

    def on_init(self):
        self.wad_data = WADData(self, map_name="E1M1")
        self.map_renderer = MapRenderer(self)
        self.player = Player(self)
        self.bsp = BSP(self)
        self.raycaster = RayCasting(self)
        self.seg_handler = SegHandler(self)
        self.view_renderer = ViewRenderer(self)
        self.object_handler = ObjectHandler(self)
        self.object_handler.add_objects_npcs()
        self.doors = {}
        # set timer to change doomguy face every 2s
        pg.time.set_timer(DOOMGUY_FACE_CHANGE_EVENT, 2000)

    def update(self):
        # reset view renderer's clip buffers, used to correctly occlude sprites
        self.view_renderer.reset_clip_buffers()
        self.player.update()
        self.object_handler.update()
        self.seg_handler.update()
        self.bsp.update()
        for door in self.doors.values():
            door.update()
        self.dt = self.clock.tick()
        pg.display.set_caption(f"{self.clock.get_fps()}")
        

    def draw(self):

        if self.map_mode:
            pg.display.flip()  # put flip here for debug draw
            self.screen.fill('black')
            self.map_renderer.draw()
        else:
            pg.surfarray.blit_array(self.screen, self.framebuffer)
            for npc in self.object_handler.npcs:
                self.view_renderer.draw_sprite(npc)
            for obj in self.object_handler.objects:
                self.view_renderer.draw_sprite(obj)
            self.view_renderer.draw_weapon(WEAPON_SPRITES[self.player.current_weapon])
            self.view_renderer.draw_status_bar()
            self.view_renderer.draw_doomguy(self.player.face_img)

            pg.display.flip()  

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                self.running = False
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    self.player.handle_action()
                elif pg.K_0 <= e.key <= pg.K_9:
                    self.player.change_weapon(chr(e.key))
                elif e.key == pg.K_n:
                    print(f"player position {self.player.pos}")
                elif e.key == pg.K_m:
                    self.map_mode = not self.map_mode
            if e.type == DOOMGUY_FACE_CHANGE_EVENT:
                self.player.set_face_image()


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
        
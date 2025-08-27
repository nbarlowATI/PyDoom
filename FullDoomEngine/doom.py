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
from weapon import Weapon

from events import *
from doomsettings import *


class DoomEngine:
    def __init__(self, wad_path="wad/DOOM1.wad"):
        self.map_mode = False
        self.debug_mode = False
        self.wad_path = wad_path
        self.screen = pg.display.set_mode(WIN_RES, pg.SCALED)
        self.framebuffer = pg.surfarray.array3d(self.screen)
        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 1 / 60

    def load(self, map_name="E1M1", difficulty=1):
        self.wad_data = WADData(self, map_name)
        self.map_renderer = MapRenderer(self)
        self.player = Player(self)
        self.weapon = Weapon(self)
        self.bsp = BSP(self)
        self.raycaster = RayCasting(self)
        self.seg_handler = SegHandler(self)
        self.view_renderer = ViewRenderer(self)
        self.object_handler = ObjectHandler(self)
        self.object_handler.add_objects_npcs(difficulty)
        self.doors = {}
        # set timer to change doomguy face every 2s
        pg.time.set_timer(DOOMGUY_FACE_CHANGE_EVENT, 2000)

    def update(self):
        # reset view renderer's clip buffers, used to correctly occlude sprites
        self.view_renderer.reset_clip_buffers()
        self.player.update()
        self.weapon.update()
        self.seg_handler.update()
        self.bsp.update()
        for door in self.doors.values():
            door.update()
        self.object_handler.update()
        self.view_renderer.update()
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
            if self.debug_mode:
                self.view_renderer.draw_z_buffer()
                self.view_renderer.draw_debug_cursor()
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
                # print some debug output
                elif e.key == pg.K_n:
                    cursor_x = int(self.view_renderer.debug_cursor[0])
                    cursor_y = int(self.view_renderer.debug_cursor[1])
                    z_val = self.view_renderer.z_buffer[cursor_x, cursor_y]
                    print(f"z-buffer {(cursor_x,cursor_y)} {z_val}")
                    barrel_dists = []
                    for obj in self.object_handler.objects:
                        if obj.sprite_name_base == "BAR1" and obj.dist:
                           
                            barrel_dists.append(obj.dist)
                    if len(barrel_dists) > 0:
                        print(f"Distance to nearest barrel {min(barrel_dists)}")
#                    print(f"player position {self.player.pos}")
                elif e.key == pg.K_m:
                    self.map_mode = not self.map_mode
                # toggle map mode
                elif e.key == pg.K_b:
                    if not self.map_mode:
                        self.debug_mode = not self.debug_mode
            # cycle randomly through the different doomguy faces
            if e.type == DOOMGUY_FACE_CHANGE_EVENT:
                self.player.set_face_image()
            # fire weapon
            if e.type == pg.MOUSEBUTTONDOWN:
                self.player.handle_fire_event(e)


    def run(self):
        while self.running:
            self.update()
            self.check_events()
            self.draw()
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        map = sys.argv[1]
    else:
        map = "E1M1"
    if len(sys.argv) > 2:
        difficulty = int(sys.argv[2])
    else:
        difficulty = 1
    game = DoomEngine()
    game.load(map, difficulty)
    game.run()
        
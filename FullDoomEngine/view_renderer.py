from numba import njit
from doomsettings import *
import random
from random import randrange as rnd
import pygame.gfxdraw as gfx


class ViewRenderer:
    def __init__(self,engine):
        self.screen = engine.screen
        self.colours = {}
        self.asset_data = engine.wad_data.asset_data
        self.palette = self.asset_data.palette
        self.sprites = self.asset_data.sprites

    def get_colour(self, tex, light_level):
        str_light = str(light_level)
        if tex + str_light not in self.colours:
            tex_id = hash(tex)
            l = light_level / 255
            random.seed(tex_id)
            rng = (50, 256)
            colour = rnd(*rng)*l, rnd(*rng)*l, rnd(*rng)*l
            self.colours[tex + str_light] = colour
        return self.colours[tex + str_light]
    
    def draw_vline(self, x, y1, y2, tex, light):
        if y1 < y2:
            gfx.vline(self.screen, x, y1, y2, self.get_colour(tex, light))


    def draw_sprite(self, sprite_name):
        img = self.sprites[sprite_name]
        pos = (H_WIDTH - img.get_width() //2, H_HEIGHT - img.get_height())
        self.screen.blit(img, pos)

    @staticmethod
    @njit
    def draw_column(framebuffer, x, y1, y2, colour):
        for iy in range(y1, y2+1):
            framebuffer[x, iy] = colour

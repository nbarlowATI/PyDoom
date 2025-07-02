from doomsettings import *
import random
from random import randrange as rnd
import pygame.gfxdraw as gfx


class ViewRenderer:
    def __init__(self,engine):
        self.screen = engine.screen
        self.colours = {}

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
        gfx.vline(self.screen, x, y1, y2, self.get_colour(tex, light))
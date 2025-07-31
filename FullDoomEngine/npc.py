import math
import pygame as pg

from enum import Enum
from doomsettings import *
from thing import Thing

class NPCState(Enum):
    standing = 0
    walking = 1
    shooting = 2
    getting_hit = 3
    dying = 4
    dead = 5



class NPC(Thing):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.engine = engine

        self.state = NPCState.standing


class ZombieMan(NPC):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = "POSS"
        self.standing_frame_suffix = "A"
        self.walking_frame_suffixes = ["B","C","D","E"]
        # base height in pixels
        self.world_height = 56
        # found by trial and error - offset to match up with ground.
        self.extra_y_offset = 20
        # cache the scaled textures.
        self.pre_cache()

    def update(self):
        super().update()


class ShotgunGuy(NPC):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = "SPOS"
        self.standing_frame_suffix = "A"
        self.walking_frame_suffixes = ["B","C","D","E"]
        # base height in pixels
        self.world_height = 56
        self.radius = 20
        # found by trial and error - offset to match up with ground.
        self.extra_y_offset = 20
        # cache the scaled textures.
        self.pre_cache()

    def update(self):
        super().update()


class Imp(NPC):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = "TROO"
        self.standing_frame_suffix = "A"
        self.walking_frame_suffixes = ["B","C","D","E"]
        # base height in pixels
        self.world_height = 56
        self.radius = 20
        # found by trial and error - offset to match up with ground.
        self.extra_y_offset = 20
        # cache the scaled textures.
        self.pre_cache()

    def update(self):
        super().update()



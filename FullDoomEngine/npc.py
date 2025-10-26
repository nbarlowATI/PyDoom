import math
import pygame as pg

from enum import Enum
from doomsettings import *
from thing import Thing

class NPCState(Enum):
    standing = 0
    walking = 1
    chasing = 2
    shooting = 3
    getting_hit = 4
    dying = 5
    dead = 6


class NPC(Thing):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.engine = engine
        self.state = NPCState.standing
        self.shootable = False
        self.line_of_sight = False

    def update(self):
        super().update()
 


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
        self.pre_cache(self.sprite_name_base)

    def update(self):
        super().update()
        if self.shootable:
            print(f"Zombieman just became shootable! {self.dist}")


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
        self.pre_cache(self.sprite_name_base)

    def update(self):
        super().update()
        if self.shootable:
            print(f"Shotgunguy just became shootable! {self.dist}")


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
        self.pre_cache(self.sprite_name_base)

    def update(self):
        super().update()
        if self.shootable:
            print("Imp just became shootable!")


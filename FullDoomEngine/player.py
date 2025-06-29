import math
from doomsettings import *
from pygame.math import Vector2 as vec2
import pygame as pg

class Player:
    def __init__(self, engine):
        self.engine = engine
        self.thing = self.engine.wad_data.things[0]
        self.pos = self.thing.pos
        self.angle = self.thing.angle - 90
        self.DIAG_MOVE_CORR = 1/math.sqrt(2)
        

    def update(self):
        self.control()
        

    def control(self):
        speed = PLAYER_SPEED * self.engine.dt
        rot_speed = PLAYER_ROT_SPEED * self.engine.dt

        key_state = pg.key.get_pressed()
        if key_state[pg.K_LEFT]:
            self.angle -= rot_speed
        if key_state[pg.K_RIGHT]:
            self.angle += rot_speed
        self.angle = self.angle % 360
        inc = vec2(0)
        if key_state[pg.K_a]:
            inc += vec2(-speed, 0)
        if key_state[pg.K_d]:
            inc += vec2(speed,0)
        if key_state[pg.K_w]:
            inc += vec2(0, speed)
        if key_state[pg.K_s]:
            inc += vec2(0, -speed)

        if inc.x and inc.y:
            inc *= self.DIAG_MOVE_CORR

        inc.rotate_ip(-self.angle)
        self.pos += inc


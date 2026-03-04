import math
import pygame as pg

from enum import Enum
from doomsettings import *
from thing import Thing
from projectile import ImpFireball

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
        self.health = 100
        self.getting_hit = False

    def update(self):
        super().update()
        if self.shootable and self.engine.weapon.shooting:
            self.health -= WEAPON_DAMAGE[self.engine.player.current_weapon]
            self.state = NPCState.getting_hit


class ZombieMan(NPC):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = "POSS"
        self.standing_frame_suffixes = ["A"]
        self.walking_frame_suffixes = ["B","C","D"]
        self.hit_frame_suffix = ["E"]
        self.dead_frame_suffixes = ["G","H", "I", "K"]
        self.gib_frame_suffixes = ["K", "L", "M"]
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
        if self.getting_hit:
            print(f"Zombieman just got hit")


class ShotgunGuy(NPC):
    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = "SPOS"
        self.standing_frame_suffixes = ["A"]
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
    TURN_RANGE = 700  # world units; Imp starts tracking the player within this distance

    def __init__(self, engine, pos, angle):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = "TROO"
        self.standing_frame_suffixes = ["A"]
        self.walking_frame_suffixes = ["B","C","D","E"]
        # base height in pixels
        self.world_height = 56
        self.radius = 20
        # found by trial and error - offset to match up with ground.
        self.extra_y_offset = 20
        # cache the scaled textures.
        self.pre_cache(self.sprite_name_base)
        self.last_fire_time = -IMP_FIRE_COOLDOWN

    def _face_player(self):
        """
        Rotate to face the player.  Derived from calculate_angle():
        rotation_index=1 (front-facing sprite toward viewer) when
            angle_diff = (angle_to_player - radians(self.angle-90)) % 2π  ≈  0
        Solving for self.angle gives:
            self.angle = 270 - degrees(atan2(dp.y, dp.x))
        where dp = player.pos - self.pos.
        """
        dp = self.engine.player.pos - self.pos
        self.angle = 270 - math.degrees(math.atan2(dp.y, dp.x))

    def _try_fire(self):
        now = pg.time.get_ticks()
        if now - self.last_fire_time < IMP_FIRE_COOLDOWN:
            return
        dp = self.engine.player.pos - self.pos
        if dp.magnitude() == 0:
            return
        direction = dp.normalize()
        # Offset spawn past the Imp's own radius so the fireball doesn't
        # immediately collide with the wall the Imp is standing against.
        spawn_pos = self.pos + direction * (self.radius + PLAYER_SIZE + 4)
        # Sample floor height at the IMP's position (not spawn_pos) so we get
        # the platform height even if the spawn offset crosses into a lower sector.
        imp_floor = self.engine.bsp.get_sub_sector_height(self.pos)
        # Place the fireball at mid-torso height (matches the Imp's visual centre).
        spawn_z = imp_floor + self.world_height - self.extra_y_offset
        # Vertical speed: glide from spawn_z to player eye height over the
        # horizontal travel distance, so the fireball arrives at the right level.
        horiz_dist = dp.magnitude()
        dz_speed = (self.engine.player.height - spawn_z) / horiz_dist * IMP_FIREBALL_SPEED
        fireball = ImpFireball(self.engine, spawn_pos, direction, spawn_z, dz_speed)
        self.engine.object_handler.projectiles.append(fireball)
        self.last_fire_time = now

    def update(self):
        super().update()
        dp = self.engine.player.pos - self.pos
        if dp.magnitude() < self.TURN_RANGE:
            self._face_player()
        if self.line_of_sight:
            self._try_fire()


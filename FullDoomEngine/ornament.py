from thing import Thing
from doomsettings import SOUNDS, WEAPON_DAMAGE
from sounds import SoundEffect


class Ornament(Thing):
    def __init__(self, engine, pos, angle, thing_info):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = thing_info["sprite_base"]
        self.world_height = float(thing_info["height"])
        self.radius = float(thing_info["radius"])
        self.pre_cache()
        self.extra_y_offset = 20

    def update(self):
        super().update()


class ExplodingBarrel(Ornament):
    def __init__(self, engine, pos, angle, thing_info):
        super().__init__(engine, pos, angle, thing_info)
        self.shootable = False
        self.line_of_sight = False
        self.health = 50
        self.extra_y_offset = 30
        self.is_exploding = False
        self.sound_effect = SoundEffect(SOUNDS["barrel_explode"], self.engine)

    def explode(self):
        self.is_exploding = True
        self.sound_effect.play()
        print("EXPLODE!!!")

    def update(self):
        super().update()
        if self.shootable:
            print(f"BARREL SHOOTABLE {self.dist}")
        if self.shootable and self.engine.weapon.shooting:
            self.health -= WEAPON_DAMAGE[self.engine.player.current_weapon]
        if self.health < 0 and not self.is_exploding:
            self.explode()

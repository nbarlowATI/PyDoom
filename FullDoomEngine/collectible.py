from thing import Thing


class Collectible(Thing):
    def __init__(self, engine, pos, angle, thing_info):
        super().__init__(engine, pos, angle)
        self.sprite_name_base = thing_info["sprite_base"]
        self.world_height = float(thing_info["height"])
        self.radius = float(thing_info["radius"])
        self.pre_cache()
        self.extra_y_offset = 20

    def update(self):
        super().update()


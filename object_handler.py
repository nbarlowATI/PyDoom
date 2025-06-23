from sprite_object import *
from npc import *

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        add_sprite(SpriteObject(game))
        add_sprite(AnimatedSprite(game))
        add_npc(SoldierNPC(game))
#        add_npc(CacoDemonNPC(game, pos=(10.5, 4.5)))
#        add_npc(CyberDemonNPC(game, pos=(9.5, 3.5)))

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        for sprite in self.sprite_list:
            sprite.update()

        for npc in self.npc_list:
            npc.update()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
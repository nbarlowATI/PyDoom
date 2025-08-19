import math
import pygame as pg
from doomsettings import SOUNDS, H_WIDTH, HEIGHT, PLAYER_STEP_FREQUENCY, WEAPON_BOB_X_AMPLITUDE, WEAPON_BOB_Y_AMPLITUDE
from sounds import SoundEffect

class Weapon:
    def __init__(self, engine):
        self.engine = engine
        self.sprite_bases = {
            "none":"PUN", 
            "pistol": "PIS", 
            "shotgun": "SHT"
        }
        self.reloading = False
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False
        self.animation_time = 30 
        self.frame_counter = 0
        self.sound_effects = {}
        for type in self.sprite_bases:
            if type in SOUNDS:
                self.sound_effects[type] = SoundEffect(SOUNDS[type], self.engine)
        self.current_weapon = "pistol"
        self.x_bob_offset = 0
        self.y__bob_offset = 0
        self.pos = (0,0)
        self.current_sprite = "PISGA0"

    def update(self):
        self.set_sprite_position()

    def set_sprite_position(self):
        x_pos = H_WIDTH - self.current_sprite.get_width() //2 + self.x_bob_offset 
        y_pos = HEIGHT - self.current_sprite.get_height() - self.engine.view_renderer.status_bar.get_height()+self.y_bob_offset + self.engine.player.weapon_y_offset
        self.pos = (x_pos, y_pos)        

    def set_current_sprite(self):
        if not self.shooting and not self.reloading:
            sprite_name = f"{self.sprite_bases[self.current_weapon]}A0"
            self.current_sprite = self.engine.view_renderer.sprites[sprite_name]

    def play_sound(self):
        current_weapon = self.engine.player.current_weapon
        if current_weapon in self.sound_effects:
            self.sound_effects[current_weapon].play()

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True


    def set_weapon_offsets(self):
        """
        Horizontal and vertical 'weapon bob' - sinusoidal oscillation
        """
        x_oscillation = WEAPON_BOB_X_AMPLITUDE * math.sin(self.step_phase * PLAYER_STEP_FREQUENCY)
        
        return self.view_height
from numba import njit
import numpy as np
from doomsettings import *
import math
import random
from random import randrange as rnd
import pygame as pg
import pygame.gfxdraw as gfx
from pygame.math import Vector2 as vec2

class ViewRenderer:
    def __init__(self,engine):
        self.engine = engine
        self.player = engine.player
        self.screen = engine.screen
        self.framebuffer = engine.framebuffer
        self.colours = {}
        self.asset_data = engine.wad_data.asset_data
        self.palette = self.asset_data.palette
        self.sprites = self.asset_data.sprites
        self.doomguy = self.asset_data.doomguy_faces
        self.status_bar = self.asset_data.status_bar
        self.textures = self.asset_data.textures
        self.sky_id = self.asset_data.sky_id
        self.sky_tex = self.asset_data.sky_tex
        self.sky_inv_scale = 160 / HEIGHT
        self.sky_tex_alt = 100
        # z-distance clipping buffer:
        # - a 2D array WIDTHxHEIGHT with each entry being the 
        # distance from the player to the nearest drawn wall at that
        # screen position.
        self.z_buffer = np.full((WIDTH, HEIGHT), np.inf)
        # debug cursor - position of a cursor that can be moved around
        # the screen, and, on demand, give e.g. z-buffer information for
        # that screen location.
        self.debug_cursor = (WIDTH//2, HEIGHT //2)

    # reset clip buffers every frame
    def reset_clip_buffers(self):
        self.z_buffer.fill(np.inf)

    def update(self):
        if self.engine.debug_mode:
            self.debug_cursor_control()

    def get_colour(self, tex, light_level):
        str_light = str(light_level)
        if tex + str_light not in self.colours:
            tex_id = hash(tex)
            random.seed(tex_id)
            colour = self.palette[rnd(0, 256)]
            colour = colour[0] * light_level, colour[1] * light_level, colour[2] * light_level
            self.colours[tex + str_light] = colour
        return self.colours[tex + str_light] 

    def draw_vline(self, x, y1, y2, tex, light):
        if y1 < y2:
            colour = self.get_colour(tex, light)
            self.draw_column(self.framebuffer, x, y1, y2, colour)

    def draw_sprite(self, sprite):
        if not sprite.scaled_sprite:
            return

        sprite_width = sprite.scaled_sprite.get_width()
        sprite_height = sprite.scaled_sprite.get_height()
        blit_x, blit_y = sprite.blit_pos

        for i in range(sprite_width):
            screen_column = blit_x + i
            if not (0 <= screen_column < WIDTH):
                continue

            sprite_col_y1 = blit_y
            sprite_col_y2 = blit_y + sprite_height

            for j in range(sprite_height):
                screen_row = blit_y + j
                if not (0 <= screen_row < HEIGHT):
                    continue

                # Check if sprite is closer than geometry at this pixel
                if sprite.dist < self.z_buffer[screen_column, screen_row]:
                    # Get the pixel colour from the sprite column
                    pixel_colour = sprite.scaled_sprite.get_at((i, j))

                    # Skip fully transparent pixels (alpha == 0)
                    if pixel_colour[:3] == COLOUR_KEY:
                        continue

                    # Draw the pixel
                    self.screen.set_at((screen_column, screen_row), pixel_colour)

    def draw_flat(self, tex_id, light_level, x, y1, y2, world_z):
        if y1 < y2:
            if tex_id == self.sky_id:
                tex_column = 2.2 * (self.player.angle + self.engine.seg_handler.x_to_angle[x])

                self.draw_wall_col(
                    self.framebuffer, self.sky_tex, tex_column, x, y1, y2,
                    self.sky_tex_alt, self.sky_inv_scale, light_level=1.0,
                )
            else:
                flat_tex = self.textures[tex_id]
                # Pass a *view* of the z-buffer column for this x
                z_col = self.z_buffer[x, y1:y2+1]
                self.draw_flat_col(self.framebuffer, flat_tex,
                                   x, y1, y2, light_level, world_z,
                                   self.player.angle, self.player.pos.x, self.player.pos.y,
                                   z_col)
                
    # draw currently selected weapon at the bottom of the screen, but above status bar.
    def draw_weapon(self, sprite_name=None):
        if sprite_name:
            img = self.sprites[sprite_name]
        else:
            img = self.engine.weapon.current_sprite
        x_pos = H_WIDTH - img.get_width() //2
        y_pos = HEIGHT - img.get_height() - self.status_bar.get_height()+self.player.weapon_y_offset
        pos = (x_pos, y_pos)
        self.screen.blit(img, pos)

    # draw the status bar at the bottom of the screen
    def draw_status_bar(self):
        img = self.status_bar
        pos = (H_WIDTH - img.get_width() //2, HEIGHT - img.get_height())
        self.screen.blit(img, pos)

    # draw the doomguy's face on the status bar.
    def draw_doomguy(self, sprite_name='STFST00'):
        img = self.doomguy[sprite_name]
        pos = (H_WIDTH - img.get_width() //2,HEIGHT - img.get_height() )
        self.screen.blit(img, pos)

    def debug_cursor_control(self):
        # if in debug mode, disable all movement
        if not self.engine.debug_mode:
            return
        speed = 0.5 * self.engine.dt

        key_state = pg.key.get_pressed()
        inc = vec2(0)
        if key_state[pg.K_LEFT]:
            inc += vec2(-speed,0)
        if key_state[pg.K_RIGHT]:
            inc += vec2(speed,0)
        if key_state[pg.K_UP]:
            inc += vec2(0, -speed)
        if key_state[pg.K_DOWN]:
            inc += vec2(0,speed)
        if inc.x and inc.y:
            inc *= 1/math.sqrt(2)
        self.debug_cursor = (self.debug_cursor[0] + inc.x, self.debug_cursor[1] + inc.y)

    def draw_debug_cursor(self):
        """
        for debugging
        """
        pg.draw.line(self.engine.screen, (255,0,0), (self.debug_cursor[0], 0), (self.debug_cursor[0], HEIGHT), 3)
        pg.draw.line(self.engine.screen, (255,0,0), (0, self.debug_cursor[1]), (WIDTH, self.debug_cursor[1]), 3)
        pg.draw.circle(self.engine.screen, 'red', (self.debug_cursor), 4)


    def draw_z_buffer(self):
        """
        For debugging
        """
        zb = self.z_buffer.copy()
        zb[np.isinf(zb)] = 999.

        # normalize to 0..255
        max_depth = np.max(zb)
        norm = (zb / max_depth) * 255
        # invert
        norm = 255 - norm
        img = norm.astype(np.uint8)
        rgb = np.repeat(img[:,:, None], 3, axis=2)
        surf = pg.surfarray.make_surface(rgb)
        self.screen.blit(surf, (0,0))




    @staticmethod
    @njit
    def draw_column(framebuffer, x, y1, y2, colour):
        for iy in range(y1, y2+1):
            framebuffer[x, iy] = colour


    @staticmethod
    @njit(fastmath=True)
    def draw_wall_col(framebuffer, tex, tex_col, x, y1, y2, tex_alt, inv_scale, light_level):
        if y1 < y2:
            tex_w, tex_h = len(tex), len(tex[0])
            tex_col = int(tex_col) % tex_w
            tex_y = tex_alt + (float(y1) - H_HEIGHT) * inv_scale

            for iy in range(y1, y2 + 1):
                col = tex[tex_col, int(tex_y) % tex_h]
                col = col[0] * light_level, col[1] * light_level, col[2] * light_level
                framebuffer[x, iy] = col
                tex_y += inv_scale

    @staticmethod
    @njit(fastmath=True)
    def draw_flat_col(screen, flat_tex, x, y1, y2, light_level, world_z,
                      player_angle, player_x, player_y, z_col):
        player_dir_x = math.cos(math.radians(player_angle))
        player_dir_y = math.sin(math.radians(player_angle))

        for i, iy in enumerate(range(y1, y2 + 1)):
            z = H_WIDTH * world_z / (H_HEIGHT - iy)
            z_col[i] = z  # store the depth in the z-buffer

            px = player_dir_x * z + player_x
            py = player_dir_y * z + player_y

            left_x = -player_dir_y * z + px
            left_y = player_dir_x * z + py
            right_x = player_dir_y * z + px
            right_y = -player_dir_x * z + py

            dx = (right_x - left_x) / WIDTH
            dy = (right_y - left_y) / WIDTH

            tx = int(left_x + dx * x) & 63
            ty = int(left_y + dy * x) & 63

            col = flat_tex[tx, ty]
            col = col[0] * light_level, col[1] * light_level, col[2] * light_level
            screen[x, iy] = col
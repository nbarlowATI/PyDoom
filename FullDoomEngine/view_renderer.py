from numba import njit
import numpy as np
from doomsettings import *
import math
import random
from random import randrange as rnd
import pygame as pg
import pygame.gfxdraw as gfx


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
        self.reset_clip_buffers()
        
    # reset clip buffers every frame
    def reset_clip_buffers(self):
        self.z_buffer = np.full((HEIGHT, WIDTH), np.inf)
        # self.clip_top = [0] * WIDTH
        # self.clip_bottom = [HEIGHT - 1] * WIDTH
        self.wall_depth = [math.inf] * WIDTH


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

            # depth clipping
            if sprite.dist > self.wall_depth[screen_column]:
                continue
            
            # try this
            # col_rect = pg.Rect(i, blit_y, 1, sprite_height)
            # sprite_col = sprite.scaled_sprite.subsurface(col_rect)
            # self.screen.blit(sprite_col, (screen_column, blit_y))

            # vertical column clipping
         #   col_clip_top = self.clip_top[screen_column]
          #  col_clip_bottom = self.clip_bottom[screen_column]

            sprite_col_y1 = blit_y
            sprite_col_y2 = blit_y + sprite_height

         #   clipped_y1 = max(sprite_col_y1, col_clip_top)
         #   clipped_y2 = min(sprite_col_y2, col_clip_bottom)
        #    visible_height = clipped_y2 - clipped_y1
         #   if visible_height > 0:
             #   src_y = clipped_y1 - sprite_col_y1
            col_rect = pg.Rect(i, 0, 1, sprite_height)
            sprite_col = sprite.scaled_sprite.subsurface(col_rect)
            self.screen.blit(sprite_col, (screen_column, blit_y))

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

                self.draw_flat_col(self.framebuffer, flat_tex,
                                   x, y1, y2, light_level, world_z,
                                   self.player.angle, self.player.pos.x, self.player.pos.y)
                
    # draw currently selected weapon at the bottom of the screen, but above status bar.
    def draw_weapon(self, sprite_name):
        img = self.sprites[sprite_name]
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

    def draw_occlusion_lines(self):
        """
        For debugging
        """
        for x in range(WIDTH):
            # ensure clip buffers are in the right range
            clip_top = int(min(max(0, self.clip_top[x]), HEIGHT-1))
            clip_bottom = int(min(max(0, self.clip_bottom[x]), HEIGHT-1))
            self.framebuffer[x, clip_top] = (255,0,0)
            self.framebuffer[x, clip_bottom] = (0,0,255)

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
                      player_angle, player_x, player_y):
        player_dir_x = math.cos(math.radians(player_angle))
        player_dir_y = math.sin(math.radians(player_angle))

        for iy in range(y1, y2 + 1):
            z = H_WIDTH * world_z / (H_HEIGHT - iy)

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
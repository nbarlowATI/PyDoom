import math
import random

from pygame.math import Vector2 as vec2
import pygame as pg

from doomsettings import *
#from door import Door


class Player:
    def __init__(self, engine):
        self.engine = engine
        self.thing = self.engine.wad_data.things[0]
        self.pos = self.thing.pos
        self.angle = self.thing.angle
        self.DIAG_MOVE_CORR = 1/math.sqrt(2)
        self.height = PLAYER_HEIGHT
        self.view_height = self.height
        self.size = PLAYER_SIZE
        self.step_phase = 0
        self.climbing_or_falling = False
        self.active_door = None
        self.current_weapon = '2'
        self.selected_weapon = '2'
        self.lowering_weapon = False
        self.raising_weapon = False
        self.health = 100
        self.face_img = 'STFST00'
        

    def get_view_height(self):
        # sinusoid with time as we step
        oscillation = PLAYER_STEP_AMPLITUDE * math.sin(self.step_phase * PLAYER_STEP_FREQUENCY)
        self.view_height = self.height + oscillation

    def get_height(self):
        target_height = PLAYER_HEIGHT + self.engine.bsp.get_sub_sector_height()
        if self.height > target_height:
            # falling
            self.climbing_or_falling = True
            fall_dist = PLAYER_FALL_SPEED * self.engine.dt
            self.height = max(self.height - fall_dist, target_height)
        elif self.height < target_height:
            # climbing
            self.climbing_or_falling = True
            climb_dist = PLAYER_CLIMB_SPEED * self.engine.dt
            self.height = min(self.height + climb_dist, target_height)
        else:
            self.height = target_height
            self.climbing_or_falling = False

    def set_face_image(self):
        if self.health > 80:
            # select randomly
            self.face_img = random.choice(
                [
                'STFST00', 'STFST01', 'STFTL10',
                'STFTR10', 'STFOUCH0', 'STFKILL0',
                'STFEVL0',
                ]
            )


    def update(self):
        self.get_height()
        self.get_view_height()
        self.control()
        self.mouse_control()
        if self.active_door:
            self.active_door.update()
        
    def change_weapon(self):
        key_state = pg.key.get_pressed()

    def control(self):
        speed = PLAYER_SPEED * self.engine.dt
        rot_speed = PLAYER_ROT_SPEED * self.engine.dt

        key_state = pg.key.get_pressed()
        if key_state[pg.K_LEFT]:
            self.angle += rot_speed
        if key_state[pg.K_RIGHT]:
            self.angle -= rot_speed
       
        inc = vec2(0)
        if key_state[pg.K_a]:
            inc += vec2(0, speed)
        if key_state[pg.K_d]:
            inc += vec2(0, -speed)
        if key_state[pg.K_w]:
            inc += vec2(speed, 0)
        if key_state[pg.K_s]:
            inc += vec2(-speed,0)

        if inc.x and inc.y:
            inc *= self.DIAG_MOVE_CORR
        if inc.magnitude() > 0 and not self.climbing_or_falling:
            self.step_phase += self.engine.dt

        inc.rotate_ip(self.angle)
        new_pos = self.pos + inc
        collision_segs = self.engine.bsp.trace_collision(self.pos, new_pos)
        if len(collision_segs) == 0:
            self.pos = new_pos
        else:
             self.pos = self.handle_collision(inc, collision_segs)

    # This function is called any time the player's movement
    # would come within some radius of a segment.  Possible outcomes are:
    # * move as normal, if segment is traversible (e.g. step, or open door)
    # * no movement, if movement is directly into non-traversible segment
    # * slide along wall, if movement is at an angle to non-traversible segment.
    def handle_collision(self, movement, collision_segs):
        pos = self.pos
        for collision_seg in collision_segs:
            wall_type = check_segment(collision_seg)
            if wall_type == WALL_TYPE.PASSABLE:
                pos += movement
            elif wall_type == WALL_TYPE.DOOR:
#                if self.active_door and self.active_door.id == collision_seg.linedef_id:
#                    if self.active_door.is_open:
                        pos+= movement
#                else:
#                    self.active_door = Door(collision_seg, self.engine)
            print(f"wall type {wall_type}")
            wall_vec = collision_seg.start_vertex - collision_seg.end_vertex
            wall_vec_norm = wall_vec / wall_vec.magnitude()
            dot_product = movement.dot(wall_vec_norm)
            pos += dot_product * wall_vec_norm
        return pos

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([H_WIDTH, H_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle -= self.rel * MOUSE_SENSITIVITY * self.engine.dt


def check_segment(segment):
    if segment.back_sector is None:
        return WALL_TYPE.SOLID_WALL
#    if segment.linedef.line_type == 1:
#        return WALL_TYPE.DOOR
    floor_diff = segment.back_sector.floor_height - segment.front_sector.floor_height
    ceiling_clearance = segment.back_sector.ceil_height - segment.back_sector.floor_height
    if floor_diff < MAX_STEP_HEIGHT and ceiling_clearance > MIN_ROOM_HEIGHT:

        print(f"middle texture {segment.linedef.back_sidedef.middle_texture}")
        return WALL_TYPE.PASSABLE
    return WALL_TYPE.IMPASSABLE

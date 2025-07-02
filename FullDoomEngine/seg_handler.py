import math
from doomsettings import *

class SegHandler:
    MAX_SCALE = 64.0
    MIN_SCALE = 0.00390625

    def __init__(self, engine):
        self.engine = engine
        self.wad_data = engine.wad_data
        self.player = engine.player

        self.seg = None
        self.rw_angle1 = None
        
        self.x_to_angle = self.get_x_to_angle_table()
        self.upper_clip, self.lower_clip = [], []

    def update(self):
        self.init_floor_ceil_clip_height()
        self.init_screen_range()

    def init_floor_ceil_clip_height(self):
        self.upper_clip = [-1 for _ in range(WIDTH)]
        self.lower_clip = [HEIGHT for _ in range(WIDTH)]


    @staticmethod
    def get_x_to_angle_table():
        x_to_angle = []
        for i in range(0, WIDTH +1):
            angle = math.degrees(math.atan((H_WIDTH -i) / SCREEN_DIST))
            x_to_angle.append(angle)
        return x_to_angle
    
    def scale_from_global_angle(self, x, rw_normal_angle, rw_distance):
        x_angle = self.x_to_angle[x]
        num = SCREEN_DIST * math.cos(math.radians(rw_normal_angle - x_angle - self.player.angle))
        den = rw_distance * math.cos(math.radians(x_angle))

        scale = num / den
        scale = min(self.MAX_SCALE, max(self.MIN_SCALE, scale))
        return scale

    def draw_solid_wall_range(self, x1, x2):
        #self.engine.view_renderer.draw_vline(x1, 0, HEIGHT) 
        seg=self.seg
        front_sector = seg.front_sector
        line = seg.linedef
        side = line.front_sidedef
        renderer = self.engine.view_renderer

        wall_texture = side.middle_texture
        ceil_texture = front_sector.ceil_texture
        floor_texture = front_sector.floor_texture
        light_level = front_sector.light_level

        world_front_z1 = front_sector.ceil_height - self.player.height
        world_front_z2 = front_sector.floor_height - self.player.height

        # check which parts to render
        b_draw_wall = side.middle_texture != '-'
        b_draw_ceil = world_front_z1 > 0
        b_draw_floor = world_front_z2 < 0

        # calculate scaling factors for left and right edges of the wall range
        rw_normal_angle = seg.angle + 90
        offset_angle = rw_normal_angle - self.rw_angle1

        hypoteneuse = math.dist(self.player.pos, seg.start_vertex)
        rw_distance = hypoteneuse * math.cos(math.radians(offset_angle))

        rw_scale1 = self.scale_from_global_angle(x1, rw_normal_angle, rw_distance)
        if x1 < x2:
            scale2 = self.scale_from_global_angle(x2, rw_normal_angle, rw_distance)
            rw_scale_step = (scale2 - rw_scale1) / (x2 - x1)
        else:
            rw_scale_step = 0
        # determine where on the screen the wall is drawn:
        wall_y1 = H_HEIGHT - world_front_z1 * rw_scale1
        wall_y1_step = -rw_scale_step * world_front_z1

        wall_y2 = H_HEIGHT - world_front_z2 * rw_scale1
        wall_y2_step = -rw_scale_step * world_front_z2

        # render
        for x in range(x1, x2+1):
            draw_wall_y1 = wall_y1 - 1
            draw_wall_y2 = wall_y2
            
            if b_draw_ceil:
                pass

            if b_draw_wall:
                wy1 = int(draw_wall_y1)
                wy2 = int(draw_wall_y2)
                renderer.draw_vline(x, wy1, wy2, wall_texture, light_level)

            if b_draw_floor:
                pass

            wall_y2 += wall_y1_step
            wall_y2 += wall_y2_step


    def init_screen_range(self):
        self.screen_range = set(range(WIDTH))

    def clip_solid_walls(self, x_start, x_end):
        if self.screen_range:
            curr_wall = set(range(x_start, x_end))
            if intersection := curr_wall & self.screen_range:
                if len(intersection) == len(curr_wall):
                    self.draw_solid_wall_range(x_start, x_end -1)
                else:
                    arr = sorted(intersection)
                    x, x2 = arr[0], arr[-1]
                    for x1, x2 in zip(arr, arr[1:]):
                        if x2 - x1 > 1:
                            self.draw_solid_wall_range(x, x1)
                            x = x2
                    self.draw_solid_wall_range(x, x2)

                self.screen_range -= intersection
        else:
            self.engine.bsp.is_traverse_bsp = False


    def classify_segment(self, segment, x1, x2, rw_angle1):
        self.seg = segment
        self.rw_angle1 = rw_angle1

        # does not cross a pixel?
        if x1 == x2: 
            return None
        
        back_sector = segment.back_sector
        front_sector = segment.front_sector

        # handle solid walls
        if back_sector is None:
            self.clip_solid_walls(x1, x2)
            return None
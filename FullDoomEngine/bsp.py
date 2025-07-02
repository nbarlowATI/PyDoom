from pygame.math import Vector2 as vec2
from doomsettings import *

class BSP:
    SUB_SECTOR_IDENTIFIER = 0x8000
    def __init__(self, engine):
        self.engine = engine
        self.player = engine.player
        self.nodes = engine.wad_data.nodes
        self.sub_sectors = engine.wad_data.sub_sectors
        self.segments = engine.wad_data.segments
        self.root_node_id = len(self.nodes) -1 
        self.is_traverse_bsp = True

    @staticmethod 
    def norm(angle):
        return angle % 360

    @staticmethod
    def angle_to_x(angle):
        if angle > 0:
            x = SCREEN_DIST - math.tan(math.radians(angle)) * H_WIDTH
        else:
            x = -math.tan(math.radians(angle)) * H_WIDTH + SCREEN_DIST
        return int(x)

    def update(self):
        self.is_traverse_bsp = True
        self.render_bsp_node(node_id=self.root_node_id)
        pass

    def add_segment_to_fov(self, vertex1, vertex2):
        angle1 = self.point_to_angle(vertex1)
        angle2 = self.point_to_angle(vertex2)
        span = self.norm(angle1 - angle2)
        # back face culling
        if span >= 180:
            return False
        rw_angle1 = angle1
        
        angle1 -= self.player.angle
        angle2 -= self.player.angle

        span1 = self.norm(angle1 + H_FOV)
        if span1 > FOV:
            if span1 >= span + FOV:
                return False
            angle1 = H_FOV
        span2 = self.norm(H_FOV - angle2)
        if span2 > FOV:
            if span2 >= span + FOV:
                return False
            angle2 = -H_FOV
        x1 = self.angle_to_x(angle1)
        x2 = self.angle_to_x(angle2)
        return x1, x2, rw_angle1




    def check_bbox(self, bbox):
        a, b = vec2(bbox.left, bbox.bottom), vec2(bbox.left, bbox.top)
        c, d = vec2(bbox.right, bbox.top), vec2(bbox.right, bbox.bottom)

        px, py = self.engine.player.pos
        if px < bbox.left:
            if py > bbox.top:
                bbox_sides = [(b, a), (c, b)]
            elif py < bbox.bottom:
                bbox_sides = [(b,a), (a,d)]
            else:
                bbox_sides = [(b,a)]
        elif px > bbox.right:
            if py > bbox.top:
                bbox_sides = [(c,d), (c,b)]
            elif py < bbox.bottom:
                bbox_sides = [(c, d), (a, d)]
            else:
                bbox_sides = [(c, d)]
        else:
            if py > bbox.top:
                bbox_sides = [(c,b)]
            elif py < bbox.bottom:
                bbox_sides = [(a,d)]
            else:
                return True
        for v1, v2 in bbox_sides:
            angle1 = self.point_to_angle(v1)
            angle2 = self.point_to_angle(v2)
            span = self.norm(angle1-angle2)

            angle1 -= self.player.angle
            span1 = self.norm(angle1 + H_FOV)
            if span1 > FOV:
                if span1 >= span + FOV:
                    continue
            return True
        return False

    def point_to_angle(self, vertex):
        delta = vertex - self.player.pos
        return math.degrees(math.atan2(delta.y, delta.x))

    def render_sub_sector(self, sub_sector_id):
        sub_sector = self.sub_sectors[sub_sector_id]
        for i in range(sub_sector.seg_count):
            seg = self.segments[sub_sector.first_seg_id + i]
            if result:= self.add_segment_to_fov(seg.start_vertex, seg.end_vertex):
                self.engine.seg_handler.classify_segment(seg, *result)
#                self.engine.map_renderer.draw_seg(seg, sub_sector_id)

    def render_bsp_node(self, node_id):
        if not self.is_traverse_bsp:
            return
        if node_id >= self.SUB_SECTOR_IDENTIFIER:
            sub_sector_id = node_id - self.SUB_SECTOR_IDENTIFIER
            self.render_sub_sector(sub_sector_id)
            return None
        node = self.nodes[node_id]
        is_on_back = self.is_on_back_side(node)
        if is_on_back:
            self.render_bsp_node(node.back_child_id)
            if self.check_bbox(node.bbox['front']):
                self.render_bsp_node(node.front_child_id)
        else:
            self.render_bsp_node(node.front_child_id)
            if self.check_bbox(node.bbox["back"]):
                self.render_bsp_node(node.back_child_id)


    def is_on_back_side(self, node):
        dx = self.player.pos.x - node.x_partition
        dy = self.player.pos.y - node.y_partition
        return dx * node.y_partition - dy * node.x_partition <= 0


# class Node:
#     def __init__(self, value):
#         self.value = value
#         self.left = None
#         self.right = None


# def insert(node, value):
#     if value < node.value:
#         if node.left:
#             insert(node.left, value)
#         else:
#             node.left = Node(value)
#     elif value > node.value:
#         if node.right:
#             insert(node.right, value)
#         else:
#             node.right = Node(value)

# def traverse(node, player_pos):
#     if node:
#         if player_pos <= node.value:
#             traverse(node.left, player_pos)
#             print(node.value, end=' ')
#             traverse(node.right, player_pos)
#         else:
#             traverse(node.right, player_pos)
#             print(node.value, end=' ')
#             traverse(node.left, player_pos)


# if __name__ == "__main__":
#     root = Node(0)
#     [insert(root, value) for value in [-15, -8, 6, 12, 20]]
#     traverse(root, player_pos=4)
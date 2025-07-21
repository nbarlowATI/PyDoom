from pygame.math import Vector2 as vec2
from doomsettings import *
from data_types import Seg
from door import Door

class RayCasting:
    def __init__(self, engine):
        self.engine = engine
        self.player = engine.player
        self.bsp = engine.bsp


    def cast_ray(self, start_pos, direction, distance):
        """
        Traverse the BSP tree, find the first segment intersected by ray.
        """
        def recurse(node_id):
            if node_id >= self.bsp.SUB_SECTOR_IDENTIFIER:
                sub_id = node_id - self.bsp.SUB_SECTOR_IDENTIFIER
                sub = self.bsp.sub_sectors[sub_id]

                closest_hit = None
                closest_t = distance + 1

                for i in range(sub.seg_count):
                    seg = self.bsp.segments[sub.first_seg_id + i]
                    result = self.intersect_ray_segment(start_pos, direction, seg.start_vertex, seg.end_vertex)
                    if result:
                        _, t = result
                        print(f"got a hit distance {t}")
                        if t < closest_t and t <= distance:
                            closest_hit = seg
                            closest_t = t
                return closest_hit
            node = self.bsp.nodes[node_id]
            # see which side of the segment we are looking at
            side = (start_pos.x - node.x_partition) * node.dy_partition - (start_pos.y - node.y_partition) * node.dx_partition <= 0

            first = node.back_child_id if side else node.front_child_id
            second = node.front_child_id if side else node.back_child_id

            result = recurse(first)
            if result:
                return result
            return recurse(second)
        return recurse(self.bsp.root_node_id)

    def find_activatable_surface(self):
        ray_start = self.player.pos
        angle_rad = math.radians(self.player.angle)
        ray_vector = vec2(math.cos(angle_rad), math.sin(angle_rad))
        print(f" aboout to cast a ray!")
        hit = self.cast_ray(ray_start, ray_vector, ACTIVATION_DIST)
        if hit:
            print(f"got a hit!!! {hit} {hit.linedef.line_type}")
            if isinstance(hit, Seg) and hit.linedef.line_type == 1:
#            if isinstance(hit, Seg) and hit.linedef.flags == 12:
                if not hit.linedef_id in self.engine.doors:
                    self.engine.doors[hit.linedef_id] = Door(hit, self.engine)
            return hit
        return None
        

    def fire_weapon(self):
        pass

    def intersect_ray_segment(self, ray_start, ray_direction, seg_start, seg_end):
        """ 
        All parameters are vec2
        Returns
            hit_position: vec2
            dist: float
        """
        ray_end = ray_start + ray_direction
        ray_dx = ray_end.x - ray_start.x
        ray_dy = ray_end.y - ray_start.y

        seg_dx = seg_end.x - seg_start.x
        seg_dy = seg_end.y - seg_start.y

        denom = ray_dx * seg_dy - ray_dy * seg_dx
        if denom == 0: # parallel lines:
            return None
        
        t1 = ((seg_start.x - ray_start.x) * seg_dy - (seg_start.y - ray_start.y) * seg_dx) / denom
        t2 = ((seg_start.x - ray_start.x) * ray_dy - (seg_start.y - ray_start.y) * ray_dx) / denom
        print(f" t1 {t1} t2 {t2} denom {denom}")
        if t1 >= 0 and 0 <= t2 <= 1:
            hit_x = ray_start.x + ray_dx * t1
            hit_y = ray_start.y + ray_dy * t1
            print(f"Got a hit {t1} {t2}")
            return vec2(hit_x, hit_y), t1
        return None


def intersect_ray_segment(ray_origin, ray_dir, seg_start, seg_end):
    """
    Check for intersection between a ray and a segment in 2D space.
    
    Parameters:
        ray_origin: vec2 - origin point of the ray
        ray_dir: vec2 - normalized direction vector of the ray
        seg_start: vec2 - start point of the segment
        seg_end: vec2 - end point of the segment

    Returns:
        Tuple (hit_point, t_ray) if intersecting, else None
    """
    # Segment vector
    v1 = ray_origin
    v2 = ray_origin + ray_dir
    v3 = seg_start
    v4 = seg_end
    # Convert to parametric form
    dx1 = v2.x - v1.x
    dy1 = v2.y - v1.y
    dx2 = v4.x - v3.x
    dy2 = v4.y - v3.y

    denom = dx1 * dy2 - dy1 * dx2
    if denom == 0:
        return None  # Parallel lines

    t1 = ((v3.x - v1.x) * dy2 - (v3.y - v1.y) * dx2) / denom
    t2 = ((v3.x - v1.x) * dy1 - (v3.y - v1.y) * dx1) / denom
    print(f" T1 {t1} T2 {t2} DENOM {denom}")
    if t1 >= 0 and 0 <= t2 <= 1:
        # Intersection point on ray and within segment
        hit_x = v1.x + dx1 * t1
        hit_y = v1.y + dy1 * t1
        return vec2(hit_x, hit_y), t1

    return None
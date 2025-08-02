from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from scene.modules.physics_body import PhysicsBody
from OpenGL.GL import *
from pygame.locals import *
from pyglm import glm
from typing import Tuple


class Collider(Module):
    requires = [Transform, PhysicsBody]

    def __init_module__(self):
        pass

    def bounding_sphere_collision(
        self, start: glm.vec3, end: glm.vec3, radius: float
    ) -> Tuple[float, glm.vec3]:

        current_distance = glm.distance(self.parent_obj.transform.position, start)
        minimal_distance = self.parent_obj.physics_body.collision_radius + glm.distance(start, end)
        # -- if collision cannot occur
        # if(current_distance <= minimal_distance):
        #    return None, glm.vec3(0)
        # -- get static sphere properties
        static_center = self.parent_obj.transform.position
        moving_radius = self.parent_obj.physics_body.collision_radius
        total_radius = moving_radius + radius

        # -- calculate movement vector and initial offset
        movement = end - start
        initial_offset = start - static_center

        # -- squared distances
        initial_dist_sq = glm.length2(initial_offset)
        total_radius_sq = total_radius * total_radius

        # -- case 1: already colliding at start position
        if initial_dist_sq <= total_radius_sq:
            if initial_dist_sq < 1e-10:  # -- centers coincide
                normal = glm.vec3(1, 0, 0)  # -- arbitrary direction
            else:
                normal = glm.normalize(initial_offset)
            return (
                -1.0,
                normal,
            )  # -- -1 so that in the physics module we can handle this case

        # -- case 2: no movement - can't collide
        movement_length_sq = glm.length2(movement)
        if movement_length_sq < 1e-10:
            return None, glm.vec3(0)

        # -- prepare quadratic equation coefficients
        A = glm.dot(movement, movement)
        B = 2 * glm.dot(movement, initial_offset)
        C = initial_dist_sq - total_radius_sq

        # -- calculate discriminant
        discriminant = B * B - 4 * A * C

        # -- no collision
        if discriminant < 0:
            return None, glm.vec3(0)

        sqrtD = glm.sqrt(discriminant)
        t1 = (-B + sqrtD) / (2 * A)
        t2 = (-B - sqrtD) / (2 * A)

        # -- find earliest valid collision in [0, 1] range
        t_collision = None
        for t in sorted([t1, t2]):
            if 0 <= t <= 1:
                t_collision = t
                break

        # -- no valid collision found
        if t_collision is None:
            return None, glm.vec3(0)

        # -- calculate collision point and normal
        collision_point = start + movement * t_collision
        normal_vec = collision_point - static_center

        # -- handle degenerate case (shouldn't happen but safe)
        if glm.length2(normal_vec) < 1e-10:
            normal = glm.vec3(1, 0, 0)
        else:
            normal = glm.normalize(normal_vec)

        return t_collision, normal

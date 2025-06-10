from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from OpenGL.GL import *
from pygame.locals import *
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from graphics.buffer import Buffer
from pyglm import glm
from graphics.graphics_backend import GraphicsBackend
from utils import custom_events
from scene.scene import Scene


class PhysicsBody(Module):
    requires = [Transform]

    def __init_module__(self):
        self.collision_radius = 0.1
        self.angular_velocity = glm.vec3(0)
        self.velocity = glm.vec3(0)
        self.subscribe_to_event(custom_events.UPDATE, self.update)
        self.subscribe_to_event(custom_events.UPDATE, self.check_collisions)

    def update(self):
        clock = GraphicsBackend().clock

        # -- velocity calculation
        delta_velocity = self.velocity * clock.delta_time
        self.parent_obj.transform.position += delta_velocity

        # -- rotation axis calculation (can be done less often)
        yaw_axis = self.parent_obj.transform.R * glm.vec3(0, 1, 0)
        pitch_axis = self.parent_obj.transform.R * glm.vec3(1, 0, 0)
        roll_axis = self.parent_obj.transform.R * glm.vec3(0, 0, -1)

        # -- rotation calculation
        delta_angular_velocity = self.angular_velocity * clock.delta_time
        pitch = glm.quat(
            glm.cos(delta_angular_velocity.x / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.x / 2)) * pitch_axis)
        )
        yaw = glm.quat(
            glm.cos(delta_angular_velocity.y / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.y / 2)) * yaw_axis)
        )
        roll = glm.quat(
            glm.cos(delta_angular_velocity.z / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.z / 2)) * roll_axis)
        )
        self.parent_obj.transform.quaternion = (
            pitch * yaw * roll * self.parent_obj.transform.quaternion
        )

        self.velocity = glm.clamp(self.velocity,-10,10)

    def check_collisions(self):
        for obj in Scene().objects:
            if (
                hasattr(obj, "collider")
                and not obj is self.parent_obj
                and 0
                < glm.distance(
                    obj.transform.position, self.parent_obj.transform.position
                )
                <= obj.mesh.bounding_sphere_radius + self.collision_radius
            ):
                distance_test: glm.vec4 = obj.collider.dist_to_point(
                    self.parent_obj.transform.position
                )
                if (
                    obj.collider.dist_to_point(self.parent_obj.transform.position).x
                    < self.collision_radius
                ):
                    self.parent_obj.transform.position += (
                        distance_test.yzw
                        / glm.length(distance_test.yzw)
                        * (self.collision_radius - distance_test.x)
                    )
                    self.velocity = glm.reflect(
                        self.velocity, distance_test.yzw / glm.length(distance_test.yzw) 
                    ) * 0.5
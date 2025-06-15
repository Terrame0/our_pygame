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
from utils.debug import debug
from scene.scene_object import SceneObject
from scene.modules.renderer import Renderer
from graphics.texture import Texture


class PhysicsBody(Module):
    requires = [Transform]

    def __init_module__(self):

        self.max_velocity = 30
        self.previous_position = glm.vec3(0)
        self.collision_radius = 0.001
        self.angular_velocity = glm.vec3(0)
        self.velocity = glm.vec3(0)
        self.subscribe_to_event(custom_events.UPDATE, self.update)
        self.subscribe_to_event(custom_events.UPDATE, self.handle_collision)

    def update(self):
        clock = GraphicsBackend().clock

        # -- velocity calculation
        delta_velocity = self.velocity * clock.delta_time
        self.previous_position = (
            self.parent_obj.transform.position
        )  # -- storing previous position
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

        if self.velocity != glm.vec3(0):
            self.velocity = glm.normalize(self.velocity) * glm.clamp(
                glm.length(self.velocity), -self.max_velocity, self.max_velocity
            )

    def handle_collision(self):
        for obj in Scene().objects:
            if hasattr(obj, "collider") and not obj is self.parent_obj:
                delta_velocity = self.velocity * GraphicsBackend().clock.delta_time
                start = self.parent_obj.transform.position
                end = self.parent_obj.transform.position + delta_velocity
                radius = obj.mesh.bounding_sphere_radius
                t, normal = obj.collider.bounding_sphere_collision(start, end, radius)
                if t is not None and normal is not None:
                    self.parent_obj.transform.position += delta_velocity * t + glm.reflect(delta_velocity,normal) * (1-t)
                    self.velocity = glm.reflect(self.velocity,normal) * 0.2
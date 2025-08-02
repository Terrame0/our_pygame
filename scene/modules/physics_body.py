from typing import Callable, List

from OpenGL.GL import *
from pyglm import glm

from scene.modules.module_base import Module
from scene.modules.transform import Transform
from scene.scene import Scene
from scene.scene_object import SceneObject

from core.clock import Clock

from utils import custom_events


class PhysicsBody(Module):
    requires = [Transform]

    def __init_module__(self, collision_radius: float = 1):

        self.max_velocity = 30
        self.previous_position = glm.vec3(0)
        self.collision_radius = collision_radius
        self.angular_velocity = glm.vec3(0)
        self.velocity = glm.vec3(0)
        self.subscribe_to_event(custom_events.UPDATE, self.update)
        self.subscribe_to_event(custom_events.UPDATE, self.handle_collision)

        self.callbacks = []
        self.collision_exclusion_list = []
        self.invert_collision_exclusion = False

    def exclude_from_collision_check(self, *objects: List[SceneObject]):
        self.collision_exclusion_list.append(*objects)

    def on_collision(self, callback: Callable[[SceneObject], None]):
        self.callbacks.append(callback)

    def update(self):
        # -- velocity calculation
        delta_velocity = self.velocity * Clock.delta_time
        self.previous_position = self.parent_obj.transform.position  # -- storing previous position
        self.parent_obj.transform.position += delta_velocity

        # -- rotation axis calculation
        yaw_axis = self.parent_obj.transform.R * glm.vec3(0, 1, 0)
        pitch_axis = self.parent_obj.transform.R * glm.vec3(1, 0, 0)
        roll_axis = self.parent_obj.transform.R * glm.vec3(0, 0, -1)

        # -- rotation calculation
        delta_angular_velocity = self.angular_velocity * Clock.delta_time
        pitch = glm.quat(
            glm.cos(delta_angular_velocity.x / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.x / 2)) * pitch_axis),
        )
        yaw = glm.quat(
            glm.cos(delta_angular_velocity.y / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.y / 2)) * yaw_axis),
        )
        roll = glm.quat(
            glm.cos(delta_angular_velocity.z / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.z / 2)) * roll_axis),
        )
        self.parent_obj.transform.quaternion = (
            pitch * yaw * roll * self.parent_obj.transform.quaternion
        )

        if self.velocity != glm.vec3(0):
            self.velocity = glm.normalize(self.velocity) * glm.clamp(
                glm.length(self.velocity), -self.max_velocity, self.max_velocity
            )

    def handle_collision(self):
        for obj in Scene.objects:
            if (
                hasattr(obj, "collider")
                and not obj is self.parent_obj
                and not ((obj in self.collision_exclusion_list) ^ self.invert_collision_exclusion)
            ):
                delta_velocity = self.velocity * Clock.delta_time
                start = self.parent_obj.transform.position
                end = self.parent_obj.transform.position + delta_velocity
                t, normal = obj.collider.bounding_sphere_collision(
                    start, end, self.collision_radius
                )
                if t is not None and normal is not None:
                    if t == -1.0:
                        self.parent_obj.transform.position += normal
                    else:
                        self.parent_obj.transform.position += delta_velocity * t + glm.reflect(
                            delta_velocity, normal
                        ) * (1 - t)
                        self.velocity = glm.reflect(self.velocity, normal) * 0.7
                        for callback in self.callbacks:
                            callback(obj)  # -- executes last because it can destroy the object
                        break

from __future__ import annotations
from core.event_system.user_events import UserEvents
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from scene.scene import Scene
from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.physics_body import PhysicsBody
from core.clock import Clock
from utils.debug import debug
from typing import List


class Projectile(Module):
    requires = [Transform, Renderer, PhysicsBody]

    def __init_module__(
        self,
        progenitor: SceneObject,
        parent_velocity: glm.vec3 = glm.vec3(0),
        exclude_from_collision: List[SceneObject] = [],
    ):
        self.parent_obj.physics_body.exclude_from_collision_check(exclude_from_collision)

        self.parent_obj.renderer.is_visible = False
        self.creation_time = Clock.now
        self.speed = 100
        self.parent_obj.physics_body.max_velocity = 100

        self.parent_obj.physics_body.velocity = (
            progenitor.transform.R * glm.vec3(0, 0, -1) * self.speed + parent_velocity
        )

        self.parent_obj.transform.position = (
            progenitor.transform.position.xyz + progenitor.transform.R * glm.vec3(0, 0, 0)
        )

        self.parent_obj.transform.scale = glm.vec3(0.5)

        self.update()
        self.subscribe_to_event(UserEvents["update"], self.update)
        self.subscribe_to_event(UserEvents["update"], self.handle_lifetime)

        self.parent_obj.physics_body.callbacks.append(self.collide_with_target)

    def collide_with_target(self, obj: SceneObject):
        if hasattr(obj, "health"):
            obj.health.value -= 1
            self.parent_obj.destroy()

    def handle_lifetime(self):
        is_alive_for = Clock.now - self.creation_time
        if is_alive_for > 0.01 and not self.parent_obj.renderer.is_visible:
            self.parent_obj.renderer.is_visible = True
            if hasattr(self.parent_obj, "trail_emitter"):
                self.parent_obj.trail_emitter.is_emitting = True
        if is_alive_for > 2:
            self.parent_obj.destroy()

    def update(self):
        self.parent_obj.transform.quaternion = Scene.camera_object.transform.quaternion

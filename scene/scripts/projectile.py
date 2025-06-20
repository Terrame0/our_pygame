from __future__ import annotations
from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from scene.scene import Scene
from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.physics_body import PhysicsBody
from core.clock import Clock


class Projectile(Module):
    requires = [Transform, Mesh, Renderer, PhysicsBody]

    def __init_module__(self, progenitor: SceneObject):
        self.parent_obj.renderer.is_visible = False
        self.progenitor = progenitor
        self.creation_time = Clock().now
        self.speed = 100
        self.parent_obj.physics_body.max_velocity = 100

        self.parent_obj.physics_body.velocity = (
            self.progenitor.physics_body.velocity
            + self.progenitor.transform.R * glm.vec3(0, 0, -1) * self.speed
        )
        self.parent_obj.transform.position = (
            self.progenitor.transform.position.xyz
            + self.progenitor.transform.R * glm.vec3(0, 0, 0)
        )

        self.parent_obj.transform.scale = glm.vec3(0.5)

        self.update()
        self.subscribe_to_event(custom_events.UPDATE, self.update)

        self.parent_obj.physics_body.callbacks.append(self.collide_with_target)

    def collide_with_target(self, obj: SceneObject):
        if hasattr(obj, "health"):
            print(obj.health.value)
            obj.health.value -= 1
            self.parent_obj.destroy()

    def update(self):
        is_alive_for = Clock().now - self.creation_time
        if is_alive_for > 0.01 and not self.parent_obj.renderer.is_visible:
            self.parent_obj.renderer.is_visible = True
            if hasattr(self.parent_obj, "trail_emitter"):
                self.parent_obj.trail_emitter.is_emitting = True
        if is_alive_for > 2:
            self.parent_obj.destroy()
        self.parent_obj.transform.quaternion = (
            Scene().camera_object.transform.quaternion
        )

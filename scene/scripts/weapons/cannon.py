from typing import List
from core.event_system.user_events import UserEvents
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.physics_body import PhysicsBody
from scene.scene_object import SceneObject
from graphics.resources.texture import Texture
from pyglm import glm
from scene.modules.module_base import Module

from scene.scripts.projectile import Projectile
from scene.scripts.trail_emitter import TrailEmitter
from core.clock import Clock
from utils.debug import debug


class Cannon(Module):
    requires = [Transform, PhysicsBody]

    def __init_module__(self):
        self.reload_time = 0.5
        self.last_shot = Clock.now - self.reload_time

        self.cannon_crosshair = SceneObject(
            name="cannon_crosshair",
            modules=[
                Transform(),
                Renderer(
                    mesh="plane.obj",
                    texture="gun_crosshair.png",
                    is_transparent=True,
                    is_UI=True,
                ),
            ],
        )

        self.subscribe_to_event(UserEvents["update"], self.update_crosshair)

    def shoot(self, owner: SceneObject):
        if pygame.mouse.get_pressed()[0] and Clock.now - self.last_shot > self.reload_time:
            self.last_shot = Clock.now
            projectile = SceneObject(
                name="projectile",
                modules=[
                    Transform,
                    PhysicsBody(collision_radius=0.3),
                    Renderer(
                        mesh="plane.obj",
                        texture="plasma.png",
                    ),
                    Projectile(
                        progenitor=self.parent_obj,
                        parent_velocity=owner.physics_body.velocity,
                        exclude_from_collision=[owner, self.parent_obj],
                    ),
                    TrailEmitter(trail_color=glm.vec3(0.470588, 0.811765, 0.203922)),
                ],
            )
            projectile.physics_body.exclude_from_collision_check(owner)

    def update_crosshair(self):
        self.cannon_crosshair.transform.position = (
            self.parent_obj.transform.position + self.parent_obj.transform.R * glm.vec3(0, 0, -100)
        )

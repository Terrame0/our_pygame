from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.physics_body import PhysicsBody
from graphics.graphics_backend import GraphicsBackend


class Projectile(Module):
    requires = [Transform, Mesh, Renderer, PhysicsBody]

    def __init_module__(self, player: SceneObject):
        self.player = player
        self.creation_time = GraphicsBackend().clock.time_snapshot
        self.speed = 100
        self.parent_obj.physics_body.max_velocity = 100

        self.parent_obj.physics_body.velocity = (
            self.player.physics_body.velocity
            + self.player.transform.R * glm.vec3(0, 0, -1) * self.speed
        )
        self.parent_obj.transform.position = (
            self.player.transform.position.xyz
            + self.player.transform.R * glm.vec3(0, -0.1, -1)
        )

        self.parent_obj.transform.scale = glm.vec3(0.5)

        self.update()
        self.subscribe_to_event(custom_events.UPDATE, self.update)

    def update(self):
        if GraphicsBackend().clock.time_snapshot - self.creation_time > 5:
            self.parent_obj.destroy()
        self.parent_obj.transform.quaternion = self.player.transform.quaternion
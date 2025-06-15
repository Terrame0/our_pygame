from graphics.graphics_backend import GraphicsBackend
from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.modules.physics_body import PhysicsBody
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module


class Enemy(Module):
    requires = [Transform, Mesh, Renderer, PhysicsBody]

    def __init_module__(self, player: SceneObject):
        self.player = player

        self.target_vector = None

        self.subscribe_to_event(custom_events.UPDATE, self.update)

    def update(self):
        self.target_vector = (
            self.player.transform.position - self.parent_obj.transform.position
        )
        self.parent_obj.transform.quaternion = glm.slerp(
            self.parent_obj.transform.quaternion,
            glm.quat(
                glm.inverse(
                    glm.lookAt(
                        self.parent_obj.transform.position,
                        self.player.transform.position,
                        self.player.transform.R * glm.vec3(0, 1, 0),
                    )
                )
            ),
            GraphicsBackend().clock.delta_time,
        )

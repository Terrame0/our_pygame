from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module


class Crosshair(Module):
    requires = [Transform,Mesh,Renderer]

    def __init_module__(self, player: SceneObject):
        self.player = player
        self.subscribe_to_event(custom_events.UPDATE, self.update)

    def update(self):
        self.parent_obj.transform.position = (
            self.player.transform.position
            + self.player.transform.R * glm.vec3(0, 0, -1)
        )
        self.parent_obj.transform.quaternion = self.player.transform.quaternion

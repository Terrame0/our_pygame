from core.event_system.user_events import UserEvents
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module


class Crosshair(Module):
    requires = [Transform, Renderer]

    def __init_module__(self, player: SceneObject):
        self.player = player
        self.subscribe_to_event(UserEvents.get_id("update"), self.update)

    def update(self):
        self.parent_obj.transform.position = (
            self.player.transform.position + self.player.transform.R * glm.vec3(0, 0, -1)
        )
        self.parent_obj.transform.quaternion = self.player.transform.quaternion

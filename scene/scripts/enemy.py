from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.modules.physics_body import PhysicsBody
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module


class Enemy(Module):
    requires = [Transform,Mesh,Renderer,PhysicsBody]

    def __init_module__(self, player: SceneObject):
        self.player = player
        self.subscribe_to_event(custom_events.UPDATE, self.update)

    def update(self):
        pass

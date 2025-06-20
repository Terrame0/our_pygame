from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.modules.physics_body import PhysicsBody
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module
from core.clock import Clock
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.projectile import Projectile
from utils.debug import debug
from graphics.texture import Texture


class Health(Module):
    def __init_module__(self, initial_value:int):
        self.value = initial_value
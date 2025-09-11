from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from scene.modules.physics_body import PhysicsBody
from OpenGL.GL import *
from pyglm import glm
from typing import Tuple
from scene.gizmos.bounding_box import AABB


class NewCollider(Module):
    requires = [Transform]

    def __init_module__(self):
        # self.node_handle = 

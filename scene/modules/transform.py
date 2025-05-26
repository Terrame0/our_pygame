import math
import numpy as np
from pyglm import glm
from scene.modules.module_base import Module


class Transform(Module):
    # -- model matrix property
    @property
    def model_matrix(self):
        if self.M == None:
            self.M = self.T * self.R * self.S
        return self.M

    # -- position property
    @property
    def position(self):
        return glm.vec3(self.T[3, 0], self.T[3, 1], self.T[3, 2])

    @position.setter
    def position(self, v: glm.vec3):
        self.T[3, 0] = v.x
        self.T[3, 1] = v.y
        self.T[3, 2] = v.z
        self.M = None

    # -- quaternion property
    @property
    def quaternion(self):
        return self.rotation_quaternion

    @quaternion.setter
    def quaternion(self, q: glm.quat):
        self.rotation_quaternion = q
        self.R = glm.mat4_cast(q)
        self.M = None

    # -- rotation property (axis angles)
    @property
    def rotation(self):
        return self.rotation_axis_angles

    @rotation.setter
    def rotation(self, v: glm.vec3):
        self.rotation_axis_angles = v
        x = math.radians(v.x)
        y = math.radians(v.y)
        z = math.radians(v.z)
        cx = math.cos(x * 0.5)
        sx = math.sin(x * 0.5)
        cy = math.cos(y * 0.5)
        sy = math.sin(y * 0.5)
        cz = math.cos(z * 0.5)
        sz = math.sin(z * 0.5)
        # -- zxy order (like in unity)
        qz = glm.quat(cz, 0, 0, sz)
        qx = glm.quat(cx, sx, 0, 0)
        qy = glm.quat(cy, 0, sy, 0)
        self.quaternion = qy * qx * qz
        self.M = None

    # -- scale property
    @property
    def scale(self):
        return glm.vec3(self.S[0, 0], self.S[1, 1], self.S[2, 2])

    @scale.setter
    def scale(self, v: glm.vec3):
        self.S[0, 0] = v.x
        self.S[1, 1] = v.y
        self.S[2, 2] = v.z
        self.M = None

    def __init_module__(
        self,
        position: glm.vec3 = glm.vec3(0, 0, 0),
        rotation: glm.vec3 = glm.vec3(0, 0, 0),
        scale: glm.vec3 = glm.vec3(1, 1, 1),
    ):

        self.T = glm.mat4()
        self.S = glm.mat4()
        self.R = glm.mat4()

        self.M = None

        self.position = position
        self.rotation = rotation
        self.scale = scale
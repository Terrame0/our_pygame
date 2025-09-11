import copy
import math
from OpenGL.GL import *
from pyglm import glm
from scene.modules.module_base import Module
from core.event_system.user_events import UserEvents
from utils.singleton_decorator import singleton
from graphics.resources.ctypes_struct import create_struct
from graphics.resources.buffer import Buffer
from scene.scene import Scene, object_data_cstruct
import numpy as np
import ctypes
import sys


class Transform(Module):

    def __init_module__(
        self,
        position: glm.vec3 = glm.vec3(0, 0, 0),
        rotation: glm.vec3 = glm.vec3(0, 0, 0),
        scale: glm.vec3 = glm.vec3(1, 1, 1),
    ):

        self.T = glm.mat4()
        self.S = glm.mat4()
        self.R = glm.mat4()
        self.object_data_mapping = object_data_cstruct.from_address(
            Scene.object_data.ctypes.data + ctypes.sizeof(object_data_cstruct) * self.parent_obj.id
        )

        # -- this flag is used to check if the model matrix
        # -- has changed and needs to be reuploaded to the gpu
        self.needs_update = True

        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.subscribe_to_event(UserEvents.get_id("update"), self.update_model_matrix)

    # -- gets called every frame to make sure the model matrix stays relevant
    def update_model_matrix(self) -> glm.mat4:
        if self.needs_update:
            self.object_data_mapping.model = self.T * self.R * self.S
            self.needs_update = False
        return self.object_data_mapping.model

    # -- model matrix property
    @property
    def model_matrix(self):
        return self.update_model_matrix()

    # -- position property
    @property
    def position(self):
        return glm.vec3(self.T[3, 0], self.T[3, 1], self.T[3, 2])

    @position.setter
    def position(self, v: glm.vec3):
        self.T[3, 0] = v.x
        self.T[3, 1] = v.y
        self.T[3, 2] = v.z
        self.needs_update = True

    # -- quaternion property
    @property
    def quaternion(self):
        return self.rotation_quaternion

    @quaternion.setter
    def quaternion(self, q: glm.quat):
        self.rotation_quaternion = q
        self.R = glm.mat4_cast(q)
        self.needs_update = True

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
        self.needs_update = True

    # -- scale property
    @property
    def scale(self):
        return glm.vec3(self.S[0, 0], self.S[1, 1], self.S[2, 2])

    @scale.setter
    def scale(self, v: glm.vec3):
        self.S[0, 0] = v.x
        self.S[1, 1] = v.y
        self.S[2, 2] = v.z
        self.needs_update = True

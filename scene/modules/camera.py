from pyglm import glm
import pygame
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from core.event_manager import EventManager
from graphics.window import Window
from graphics.resources.buffer import Buffer
from OpenGL.GL import *
from graphics.resources.ctypes_struct import create_struct
import numpy as np
from utils import custom_events


camera_data_cstruct = create_struct(
    projection=glm.mat4,
    view=glm.mat4,
    window_size=glm.vec2,
    view_vector=glm.vec4,
)


class Camera(Module):
    requires = [Transform]

    def __init_module__(self, *args, **kwargs):
        self.aspect_ratio = Window.aspect_ratio
        self.near_plane = 0.1
        self.far_plane = 1000
        self._fov_radians = glm.radians(70)

        # -- uniform buffer
        self.camera_ubo = Buffer(GL_UNIFORM_BUFFER)
        self.camera_ubo.upload_data(np.zeros(1, dtype=camera_data_cstruct))
        self.camera_data = self.camera_ubo.map_to_cstruct(camera_data_cstruct)

        self._projection_matrix = glm.perspective(
            glm.radians(70), self.aspect_ratio, self.near_plane, self.far_plane
        )

        self.load_projection_matrix_to_gpu()
        self.load_view_matrix_to_gpu()
        self.load_view_vector_to_gpu()
        self.load_window_size_to_gpu()

        EventManager.subscribe(pygame.VIDEORESIZE, self._resize, pass_event=True)
        EventManager.subscribe(custom_events.UPDATE, self.load_view_matrix_to_gpu)
        EventManager.subscribe(custom_events.UPDATE, self.load_view_vector_to_gpu)

    def load_view_matrix_to_gpu(self):  # -- is called every frame
        self.camera_data.view = self.view_matrix

    def load_view_vector_to_gpu(self):  # -- is called every frame
        self.camera_data.view_vector = glm.vec4(self.parent_obj.transform.R * glm.vec3(0, 0, -1), 1)

    def load_projection_matrix_to_gpu(self):  # -- is called on window size or fov change
        self.camera_data.projection = self.projection_matrix

    def load_window_size_to_gpu(self):  # -- is called on window size change
        self.camera_data.window_size = glm.vec2(*Window.size)

    def _resize(self, event):
        self.aspect_ratio = event.size[0] / event.size[1]
        self._projection_matrix = glm.perspective(
            self._fov_radians,
            self.aspect_ratio,
            self.near_plane,
            self.far_plane,
        )
        self.load_projection_matrix_to_gpu()
        self.load_window_size_to_gpu()

    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def fov(self):
        return glm.degrees(self._fov_radians)

    @fov.setter
    def fov(self, fov: float):
        self._fov_radians = glm.radians(fov)
        self._projection_matrix = glm.perspective(
            self._fov_radians,
            self.aspect_ratio,
            self.near_plane,
            self.far_plane,
        )
        self.load_projection_matrix_to_gpu()

    @property
    def view_matrix(self):
        self._view_matrix = glm.inverse(self.parent_obj.transform.model_matrix)
        return self._view_matrix

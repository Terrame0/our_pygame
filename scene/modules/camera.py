from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform

# -- TODO add enter and exit methods (to automatically bind the camera)


class Camera(Module):
    requires = [Transform]

    def __init_module__(self, *args, **kwargs):
        self.aspect_ratio = 800 / 600
        self.near_plane = 0.1
        self.far_plane = 1000
        self._fov = glm.radians(70)
        self._projection_matrix = glm.perspective(
            glm.radians(70), self.aspect_ratio, self.near_plane, self.far_plane
        )

    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, fov: float):
        self._fov = fov
        self._projection_matrix = glm.perspective(
            glm.radians(fov),
            self.aspect_ratio,
            self.near_plane,
            self.far_plane,
        )

    @property
    def view_matrix(self):
        self._view_matrix = glm.inverse(self.parent_obj.transform.model_matrix)
        return self._view_matrix

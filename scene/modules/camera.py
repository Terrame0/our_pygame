from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform

# -- TODO add enter and exit methods (to automatically bind the camera)


class Camera(Module):
    requires = [Transform]

    def __init_module__(self, *args, **kwargs):
        self._projection_matrix = glm.perspective(
            glm.radians(90), 800/600, 0.001, 1000
        )
        self._view_matrix = glm.vec3(0, 0, 1)
    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def view_matrix(self):
        self._view_matrix = glm.inverse(self.parent_obj.transform.model_matrix)
        return self._view_matrix

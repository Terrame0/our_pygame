from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform

# -- TODO add enter and exit methods (to automatically bind the camera)


class Camera(Module):
    requires = [Transform]

    def __init_module__(self, *args, **kwargs):
        self._projection_matrix = glm.perspective(
            glm.radians(90), 800/600, 0.1, 10
        )
        self._view_matrix = glm.vec3(0, 0, 1)
    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def view_matrix(self):
        transform = self.parent_modules[Transform.__name__]
        self._view_matrix = glm.inverse(transform.model_matrix)
        #self._view_matrix = glm.mat4(1)
        #for axis_id, angle in zip(
        #    ["z", "x", "y"],
        #    [transform.rotation[2], transform.rotation[0], transform.rotation[1]],
        #):
        #    axis = glm.vec3(0)
        #    setattr(axis, axis_id, 1)
        #    self._view_matrix = glm.rotate(self._view_matrix, glm.radians(angle), axis)
        #self._view_matrix[3, 0] = transform.position.x
        #self._view_matrix[3, 1] = transform.position.y
        #self._view_matrix[3, 2] = transform.position.z
        return self._view_matrix

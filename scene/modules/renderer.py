from scene.modules.module_base import Module
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from OpenGL.GL import *
from graphics.buffer import Buffer
import glm


class Renderer(Module):
    requires = [Mesh, Transform]

    def __init_module__(self):

        self.mesh = self.parent_modules[Mesh.__name__]
        self.transform = self.parent_modules[Transform.__name__]

        # -- vertex array object
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # -- vertex buffer
        vbo = Buffer(GL_ARRAY_BUFFER, GL_STATIC_DRAW)
        vbo.upload_data(self.mesh.vertex_buffer)

        # -- element buffer
        ebo = Buffer(GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW)
        ebo.upload_data(self.mesh.index_buffer)

        # -- vertex attributes
        with vbo, ebo:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, None)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(
                1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4)
            )
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(
                2, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(5 * 4)
            )
            glEnableVertexAttribArray(2)
            glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(1, 1, False, glm.value_ptr(self.transform.model_matrix))
        glDrawElements(GL_TRIANGLES, len(self.mesh.index_buffer), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
from scene.modules.module_base import Module
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from OpenGL.GL import *
from graphics.buffer import Buffer
from graphics.texture import Texture
import glm


class Renderer(Module):
    requires = [Mesh, Transform]

    def __init_module__(
        self,
        texture: Texture = None,
        is_transparent: bool = False,
        is_UI: bool = False,
        is_visible: bool = True,
    ):

        # -- properties
        self.is_transparent = is_transparent
        self.is_UI = is_UI
        self.is_visible = is_visible

        # -- resources
        self.mesh = self.parent_obj.mesh
        self.transform = self.parent_obj.transform
        self.shader_program = None
        self.texture = texture

        # -- vertex array object
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # -- vertex buffer
        vbo = Buffer(GL_ARRAY_BUFFER)
        vbo.upload_data(self.mesh.vertex_buffer, usage=GL_STATIC_DRAW)

        # -- element buffer
        ebo = Buffer(GL_ELEMENT_ARRAY_BUFFER)
        ebo.upload_data(self.mesh.index_buffer, usage=GL_STATIC_DRAW)

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
        if self.is_UI:
            glDisable(GL_DEPTH_TEST)
        else:
            glEnable(GL_DEPTH_TEST)
        if self.texture != None:
            self.texture.bind()
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(1, 1, False, glm.value_ptr(self.transform.model_matrix))
        glDrawElements(GL_TRIANGLES, len(self.mesh.index_buffer), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
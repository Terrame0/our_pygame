from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from OpenGL.GL import *
from pygame.locals import *
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from graphics.buffer import Buffer
from pyglm import glm


class Collider(Module):
    requires = [Transform, Mesh]

    def __init_module__(self, obj_path: str = ""):
        self.mesh = self.parent.mesh

        self.collision_checker = Shader(
            "graphics/shaders/collision_checker.glsl", GL_COMPUTE_SHADER
        )
        self.compute_program = ShaderProgram(self.collision_checker)

        self.vertices = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.vertices.bind_base(0)
        self.indices = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.indices.bind_base(1)
        self.result = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.result.bind_base(2)

        self.upload_buffers()

    # -- TODO find a way to update on mesh change
    def upload_buffers(self):
        self.vertices.upload_data(self.mesh.vertex_buffer, usage=GL_DYNAMIC_DRAW)
        self.indices.upload_data(self.mesh.index_buffer, usage=GL_DYNAMIC_DRAW)
        self.result.upload_data(
            glm.array([glm.vec4(0)] * (len(self.mesh.index_buffer) // 3)),
            usage=GL_DYNAMIC_COPY,
        )

    def dist_to_point(self, pos):
        with self.compute_program:
            glUniform3fv(0, 1, glm.value_ptr(pos))
            glDispatchCompute((self.indices.size // 3) // 64 + 1, 1, 1)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
        min_distance = min(self.result.get_data(), key=lambda x: x[0])
        return min_distance
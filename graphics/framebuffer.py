from OpenGL.GL import *
from graphics.shader import Shader
from utils.gl_constant_map import get_gl_name
from utils.debug import debug


class Framebuffer:
    def __init__(self):
        self.id = glGenFramebuffers(1)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.id)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
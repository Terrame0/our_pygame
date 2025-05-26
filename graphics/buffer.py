from OpenGL.GL import *
from utils.gl_constant_map import get_gl_name
import numpy as np
from utils.debug import debug


class Buffer:
    def __init__(self, target, usage=GL_STATIC_DRAW):
        self.id = glGenBuffers(1)
        self.target = target
        self.size = 0
        self.usage = usage
        debug.log(f"constructing a {get_gl_name(int(target))} at index {self.id}")

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        glBindBuffer(self.target, self.id)

    def unbind(self):
        glBindBuffer(self.target, 0)

    def upload_data(self, data: np.ndarray, usage=GL_STATIC_DRAW):
        self.usage = usage
        self.size = data.nbytes
        with self:
            glBufferData(self.target, data.nbytes, data, self.usage)

    def delete(self):
        glDeleteBuffers(self.id)
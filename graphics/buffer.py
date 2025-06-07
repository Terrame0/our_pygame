from OpenGL.GL import *
from utils.gl_constant_map import get_gl_name
import numpy as np
from typing import Any, Type, List
from utils.debug import debug
import sys
from pyglm import glm
import pickle


class Buffer:
    def __init__(self, target):
        self.id = glGenBuffers(1)
        self.target = target
        self.usage = None
        self.size = None
        self.nbytes = None
        self.element_type = None
        debug.log(f"constructing a {get_gl_name(int(target))} at index {self.id}")

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        glBindBuffer(self.target, self.id)

    def bind_base(self, slot: int):
        with self as buffer:
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER, slot, buffer.id)

    def unbind(self):
        glBindBuffer(self.target, 0)

    def upload_data(self, data: glm.array, usage=GL_STATIC_DRAW):
        if not isinstance(data,glm.array):
            raise TypeError("(!) must be a glm array")
        if len(data) == 0:
            raise Error("(!) the array cannot be empty")

        self.element_type = data.element_type
        self.usage = usage
        self.size = len(data)
        self.nbytes = data.nbytes
        with self:
            glBufferData(self.target, data.nbytes, data.ptr, self.usage)

    def get_data(self):
        data = glm.array([self.element_type()]*self.size)
        glGetNamedBufferSubData(self.id, 0, self.nbytes, data.ptr)
        return data

    def delete(self):
        glDeleteBuffers(self.id)
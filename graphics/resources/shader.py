from OpenGL.GL import *
from utils.gl_constant_map import get_gl_name
from utils.debug import debug
from utils.path_resolver import resolve_path


class Shader:
    def __init__(self, path, shader_type):
        self.id = glCreateShader(shader_type)
        self.path = path
        self.shader_type = shader_type
        debug.log(f"constructing a {self}")
        glShaderSource(self.id, open(resolve_path(path), "r").read())
        glCompileShader(self.id)

        if not glGetShaderiv(self.id, GL_COMPILE_STATUS):
            raise Exception(f"(!) error during shader construction:{glGetShaderInfoLog(self.id)}")

    def __str__(self):
        return f"[{get_gl_name(int(self.shader_type))}] [{self.id}] (path: {self.path})"

    def delete(self):
        glDeleteShader(self.id)

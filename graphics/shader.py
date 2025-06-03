from OpenGL.GL import *
from utils.gl_constant_map import get_gl_name
from utils.debug import debug
from utils.path_resolver import resolve_path


class Shader:
    def __init__(self, path, type):
        self.id = glCreateShader(type)
        debug.log(
            f"constructing a {get_gl_name(int(type))} at {path} at index {self.id}"
        )
        glShaderSource(self.id, open(resolve_path(path), "r").read())
        glCompileShader(self.id)

        if not glGetShaderiv(self.id, GL_COMPILE_STATUS):
            raise Exception(
                f"(!) error during shader construction:{glGetShaderInfoLog(self.id)}"
            )

    def delete(self):
        glDeleteShader(self.id)
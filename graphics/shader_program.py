from OpenGL.GL import *
from graphics.shader import Shader
from utils.gl_constant_map import get_gl_name
from utils.debug import debug


class ShaderProgram:
    def __init__(self, *shader_list: tuple[Shader, ...]):
        self.id = glCreateProgram()
        self.shader_list = shader_list
        debug.log(f"constructing a shader program with:")
        debug.indent()
        for x in shader_list:
            debug.log(get_gl_name(glGetShaderiv(x.id, GL_SHADER_TYPE)))
        debug.dedent()
        debug.log(f"at index {self.id}")

        for shader in self.shader_list:
            glAttachShader(self.id, shader.id)
        glLinkProgram(self.id)
        # -- check if construction failed
        if not glGetProgramiv(self.id, GL_LINK_STATUS):
            raise Exception(
                f"(!) error during program construction:{glGetProgramInfoLog(self.id)}"
            )

    def __enter__(self):
        self.use()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        glUseProgram(0)

    def use(self):
        glUseProgram(self.id)

    def delete(self):
        glDeleteProgram(self.id)
        for shader in self.shader_list:
            shader.delete()
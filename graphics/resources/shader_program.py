from OpenGL.GL import *
from graphics.resources.shader import Shader
from graphics.loaders.shader_loader import ShaderLoader
from utils.gl_constant_map import get_gl_name
from utils.debug import debug


class ShaderProgram:
    def __init__(self, *shader_name_list: tuple[str, ...]):
        self.id = glCreateProgram()
        self.shader_list = [ShaderLoader[name] for name in shader_name_list]
        debug.log(f"constructing a {self} with:")
        debug.indent()
        for shader in self.shader_list:
            debug.log(f"{shader}")
        debug.dedent()

        for shader in self.shader_list:
            glAttachShader(self.id, shader.id)
        glLinkProgram(self.id)
        # -- check if construction failed
        if not glGetProgramiv(self.id, GL_LINK_STATUS):
            raise Exception(f"(!) error during program construction:{glGetProgramInfoLog(self.id)}")

    def get_uniform_id(self, name: str):
        return glGetUniformLocation(self.id, name)

    def get_ssbo_id(self, name: str):
        index = glGetProgramResourceIndex(self.id, GL_SHADER_STORAGE_BLOCK, name)

        if index == GL_INVALID_INDEX:
            raise RuntimeError(f"(!) SSBO block '{name}' not found")

        props = [GL_BUFFER_BINDING]
        output = glGetProgramResourceiv(
            self.id,
            GL_SHADER_STORAGE_BLOCK,
            index,
            len(props),
            props,
            1,
        )

        return output[1]

    def __str__(self):
        return f"[{self.__class__.__name__}] [{self.id}]"

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

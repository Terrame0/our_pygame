import pygame
from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.scene import Scene
from utils.debug import debug
from pyglm import glm
import time
from graphics.texture import Texture


@singleton
class GraphicsBackend:

    def __init__(self):
        debug.log("initializing graphics backend")
        debug.indent()

        # -- fields
        self.display = (800, 600)
        self.projection = glm.perspective(
            glm.radians(90), self.display[0] / self.display[1], 0.1, 10
        )

        # -- pygame setup
        pygame.init()
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)

        # -- opengl setup
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        self.fragment_shader = Shader(
            "graphics/shaders/fragment.glsl", GL_FRAGMENT_SHADER
        )
        self.vertex_shader = Shader("graphics/shaders/vertex.glsl", GL_VERTEX_SHADER)
        self.shader_program = ShaderProgram((self.fragment_shader, self.vertex_shader))

        debug.dedent()
        debug.log("graphics backend initialization complete")

        self.texture = Texture("texture.jpg")
        glUseProgram(self.shader_program.id)

    def next_frame(self, scene: Scene):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUniformMatrix4fv(2, 1, False, glm.value_ptr(self.projection))
        with self.texture:
            for obj in scene.object_list:
                if hasattr(obj, "renderer"):
                    obj.renderer.draw()
        pygame.display.flip()
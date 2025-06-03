import pygame
from utils import custom_events
from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from scene.scene import Scene
from utils.debug import debug
from pyglm import glm
import time
from graphics.texture import Texture
from graphics.clock import Clock


@singleton
class GraphicsBackend:

    def __init__(self):
        debug.log("initializing graphics backend")
        debug.indent()

        self.clock = Clock()

        # -- pygame setup
        pygame.init()
        pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

        # -- opengl setup
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self.fragment_shader = Shader(
            "graphics/shaders/fragment.glsl", GL_FRAGMENT_SHADER
        )
        self.vertex_shader = Shader("graphics/shaders/vertex.glsl", GL_VERTEX_SHADER)
        self.shader_program = ShaderProgram((self.fragment_shader, self.vertex_shader))

        debug.dedent()
        debug.log("graphics backend initialization complete")

        # -- TODO make this not hard-coded
        self.texture = Texture("assets/cat_tex.png")
        glUseProgram(self.shader_program.id)
        glUniform2fv(0, 1, pygame.display.get_window_size())

    def next_frame(self, scene: Scene):
        pygame.event.post(pygame.event.Event(custom_events.UPDATE))
        self.clock.tick()
        pygame.time.Clock().tick(144)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniformMatrix4fv(2, 1, False, glm.value_ptr(scene.camera.projection_matrix))
        glUniformMatrix4fv(3, 1, False, glm.value_ptr(scene.camera.view_matrix))

        with self.texture:
            for obj in scene.object_list:
                if hasattr(obj, "renderer"):
                    obj.renderer.draw()
        pygame.display.flip()
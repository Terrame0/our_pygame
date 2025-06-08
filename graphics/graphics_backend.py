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
from graphics.texture import Texture
from graphics.clock import Clock
from core.event_manager import EventManager


@singleton
class GraphicsBackend:

    def __init__(self):
        debug.log("initializing graphics backend")
        debug.indent()

        self.clock = Clock()

        # -- pygame setup
        pygame.init()
        pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        EventManager().subscribe(
            pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False
        )
        EventManager().subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

        # -- opengl setup
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self.fragment_shader = Shader(
            "graphics/shaders/fragment.glsl", GL_FRAGMENT_SHADER
        )
        self.vertex_shader = Shader("graphics/shaders/vertex.glsl", GL_VERTEX_SHADER)
        self.render_program = ShaderProgram(self.fragment_shader, self.vertex_shader)

        debug.dedent()
        debug.log("graphics backend initialization complete")

        # -- TODO make this not hard-coded
        glUseProgram(self.render_program.id)
        glUniform2fv(0, 1, pygame.display.get_window_size())

    def next_frame(self):

        pygame.event.post(pygame.event.Event(custom_events.UPDATE))
        self.clock.tick()
        pygame.time.Clock().tick(144)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        with self.render_program:
            glUniformMatrix4fv(
                2, 1, False, glm.value_ptr(Scene().camera.projection_matrix)
            )
            glUniformMatrix4fv(3, 1, False, glm.value_ptr(Scene().camera.view_matrix))
            transparent_objects = []
            for obj in Scene().objects:
                if hasattr(obj, "renderer") and obj.renderer.is_visible:
                    # -- UI faces the camera and is of constant size relative to view
                    if obj.renderer.is_UI:
                        obj.transform.quaternion = (
                            Scene().camera_object.transform.quaternion
                        )
                        obj.transform.scale = (
                            glm.vec3(
                                glm.distance(
                                    obj.transform.position,
                                    Scene().camera_object.transform.position,
                                )
                            )
                            * 0.1
                        )

                    if not obj.renderer.is_transparent:
                        obj.renderer.draw()
                    else:
                        transparent_objects.append(obj)
            transparent_objects.sort(
                key=lambda obj: glm.distance(
                    obj.transform.position, Scene().camera_object.transform.position
                ),
                reverse=True,
            )
            for obj in transparent_objects:
                obj.renderer.draw()

        pygame.display.flip()
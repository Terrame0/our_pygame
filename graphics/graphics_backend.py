import pygame
from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from scene.scene import Scene
from utils.debug import debug
from pyglm import glm
from graphics.texture import Texture
from graphics.framebuffer import Framebuffer
from core.clock import Clock
from core.event_manager import EventManager
from graphics.buffer import Buffer
from graphics.particle_system import ParticleSystem


@singleton
class GraphicsBackend:

    def __init__(self):
        debug.log("initializing graphics backend")
        debug.indent()

        self.clock = Clock()

        # -- pygame setup
        pygame.init()
        pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

        # -- window focus whatevers
        EventManager().subscribe(
            pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False
        )
        EventManager().subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

        # -- global opengl state
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # -- shader program that renders geometry
        self.geometry_shader_program = ShaderProgram(
            Shader(
                "graphics/shaders/geometry_rendering/gmt_fragment.glsl",
                GL_FRAGMENT_SHADER,
            ),
            Shader(
                "graphics/shaders/geometry_rendering/gmt_vertex.glsl", GL_VERTEX_SHADER
            ),
        )

        glUseProgram(self.geometry_shader_program.id)
        glUniform2fv(0, 1, pygame.display.get_window_size())

        # -- texture that geometry is rendered to
        self.geometry_texture = Texture((800, 600))

        # -- depth texture to access in compute shaders
        self.depth_texture = Texture(
            (800, 600),
            internal_format=GL_DEPTH_COMPONENT32,
            pixel_data_format=GL_DEPTH_COMPONENT,
            pixel_component_format=GL_FLOAT,
        )

        # -- custom framebuffer (to write directly to its texture)
        self.geometry_fbo = Framebuffer()
        with self.geometry_fbo:
            glFramebufferTexture2D(  # -- binding the screen texture
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_2D,
                self.geometry_texture.id,
                0,
            )

            glFramebufferTexture2D(  # -- binding the depth texture
                GL_FRAMEBUFFER,
                GL_DEPTH_ATTACHMENT,
                GL_TEXTURE_2D,
                self.depth_texture.id,
                0,
            )

        # -- shader program to render the texture to the default pygame framebuffer
        self.texture_to_screen_program = ShaderProgram(
            Shader(
                "graphics/shaders/texture_to_screen/tts_fragment.glsl",
                GL_FRAGMENT_SHADER,
            ),
            Shader(
                "graphics/shaders/texture_to_screen/tts_vertex.glsl", GL_VERTEX_SHADER
            ),
        )

        debug.dedent()
        debug.log("graphics backend initialization complete")

    def next_frame(self):
        pygame.time.Clock().tick(144)

        self.render_geometry()
        ParticleSystem().render_particles(self.geometry_fbo)

        self.render_texture_to_screen(self.geometry_texture)
        pygame.display.flip()

    def render_texture_to_screen(self, texture: Texture):
        glBindFramebuffer(
            GL_FRAMEBUFFER, 0
        )  # -- rendering a fullscreen triangle to the default framebuffer

        with self.texture_to_screen_program, texture:
            glDisable(GL_DEPTH_TEST)
            glDrawArrays(GL_TRIANGLES, 0, 3)

    # -- TODO refactor this PLEASE
    def render_geometry(self):
        with self.geometry_shader_program, self.geometry_fbo:  # -- rendering to a custom framebuffer
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # -- setting camera matrices
            glUniformMatrix4fv(
                2, 1, False, glm.value_ptr(Scene().camera.projection_matrix)
            )
            glUniformMatrix4fv(3, 1, False, glm.value_ptr(Scene().camera.view_matrix))

            # -- transparency checks (TODO move this crap to a separate method)
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

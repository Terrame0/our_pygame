from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from pyglm import glm
from graphics.framebuffer import Framebuffer


@singleton
class Blitter:
    def __init__(self):
        # -- shader program that merges two framebuffers together accounting for depth
        self.blitter_program = ShaderProgram(
            Shader(
                "graphics/shaders/misc/blitter.comp",
                GL_COMPUTE_SHADER,
            )
        )

        # -- shader program that renders a texture to the default framebuffer
        self.texture_to_screen_program = ShaderProgram(
            Shader(
                "graphics/shaders/misc/texture_to_screen/tts.frag",
                GL_FRAGMENT_SHADER,
            ),
            Shader(
                "graphics/shaders/misc/texture_to_screen/tts.vert", GL_VERTEX_SHADER
            ),
        )

    def blit_to_default_framebuffer(self, source: Framebuffer):
        glBindFramebuffer(
            GL_FRAMEBUFFER, 0
        )  # -- rendering a fullscreen triangle to the default framebuffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        with self.texture_to_screen_program, source.color_attachment.unit(0):
            glDisable(GL_DEPTH_TEST)
            glDrawArrays(GL_TRIANGLES, 0, 3)

    def merge_framebuffers(self, source: Framebuffer, target: Framebuffer):
        with self.blitter_program, source.depth_attachment.unit(0), target.depth_attachment.unit(1):
            source.color_attachment.bind_as_image(0)
            target.color_attachment.bind_as_image(1)
            source_size = source.color_attachment.size
            target_size = target.color_attachment.size
            glUniform2fv(0, 1, glm.value_ptr(glm.vec2(*source_size)))
            glUniform2fv(1, 1, glm.value_ptr(glm.vec2(*target_size)))
            dispatch_size = (
                min(source_size[0], target_size[0]),
                min(source_size[1], target_size[1]),
            )
            glDispatchCompute(dispatch_size[0] // 8 + 1, dispatch_size[1] // 8 + 1, 1)

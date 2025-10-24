from OpenGL.GL import *
from utils.singleton_decorator import singleton
from graphics.resources.shader import Shader
from graphics.resources.shader_program import ShaderProgram
from pyglm import glm
from graphics.resources.framebuffer import Framebuffer
from graphics.window import Window
from scene.scene import Scene


@singleton
class Blitter:
    def __init__(self):
        # -- shader program that merges two framebuffers together accounting for depth
        self.merge_program = ShaderProgram(
            "framebuffer_merge.comp",
        )

        # -- shader program that renders a texture to the default framebuffer
        self.transparency_resolver = ShaderProgram(
            "blitter.frag",
            "blitter.vert",
        )

    def blit_to_screen(self, source: Framebuffer):
        glBindFramebuffer(
            GL_FRAMEBUFFER, 0
        )  # -- rendering a fullscreen triangle to the default framebuffer
        Scene.camera.camera_ubo.bind_base(0, GL_UNIFORM_BUFFER)  # -- camera ubo
        with (
            self.transparency_resolver,
            source.accumulation_attachment.unit(0),
            source.revealage_attachment.unit(1),
            source.color_attachment.unit(2),
        ):
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_DEPTH_TEST)
            glDrawArrays(GL_TRIANGLES, 0, 3)
            glEnable(GL_DEPTH_TEST)

    # def merge_framebuffers(self, source: Framebuffer, target: Framebuffer):
    #    with self.merge_program, source.depth_attachment.unit(0), target.depth_attachment.unit(1):
    #        source.color_attachment.bind_as_image(0)
    #        target.color_attachment.bind_as_image(1)
    #        source_size = source.color_attachment.size
    #        target_size = target.color_attachment.size
    #        glUniform2fv(0, 1, glm.value_ptr(glm.vec2(*source_size)))
    #        glUniform2fv(1, 1, glm.value_ptr(glm.vec2(*target_size)))
    #        dispatch_size = (
    #            int(min(source_size[0], target_size[0])),
    #            int(min(source_size[1], target_size[1])),
    #        )
    #        glDispatchCompute(dispatch_size[0] // 8 + 1, dispatch_size[1] // 8 + 1, 1)

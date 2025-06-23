from OpenGL.GL import *
from graphics.texture import Texture


class Framebuffer:
    def __init__(self):
        self.id = glGenFramebuffers(1)
        self._color_attachment: Texture = None
        self._depth_attachment: Texture = None

    @property
    def color_attachment(self):
        return self._color_attachment

    @color_attachment.setter
    def color_attachment(self, texture: Texture):
        self._color_attachment = texture
        with self:
            glFramebufferTexture2D(  # -- binding the screen texture
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_2D,
                self._color_attachment.id,
                0,
            )

    @property
    def depth_attachment(self):
        return self._depth_attachment

    @depth_attachment.setter
    def depth_attachment(self, texture: Texture):
        self._depth_attachment = texture
        with self:
            glFramebufferTexture2D(  # -- binding the depth texture
                GL_FRAMEBUFFER,
                GL_DEPTH_ATTACHMENT,
                GL_TEXTURE_2D,
                self._depth_attachment.id,
                0,
            )

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.id)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

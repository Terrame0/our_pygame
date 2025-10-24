from typing import Tuple, Dict

from OpenGL.GL import *


from graphics.resources.texture import Texture
from graphics.window import Window

from core.event_manager import EventManager
from utils.debug import debug


class Framebuffer:
    def __init__(self, **textures):

        self.attachments: Dict[str, Tuple[Texture, int]] = {}
        self.id = glGenFramebuffers(1)

        for name, value in textures.items():
            setattr(self, name, value)

        # EventManager.subscribe(pygame.VIDEORESIZE, self.resize, pass_event=True)

    # -- checks if the value is a color attachment, if true binds it to the framebuffer and adds it to the list, otherwise passes it through
    def __setattr__(self, name, value):
        if isinstance(value, Texture):
            if not hasattr(value, "attachment_type"):
                debug.log("(*) provided texture is not an attachment")
            else:
                texture = value
                self.attachments[name] = texture
                if texture.size != Window.size:
                    raise RuntimeError(
                        f"(!) framebuffer color attachment size mismatch! (should be {' by '.join(map(str,Window.size))}, but received {' by '.join(map(str,texture.size))})"
                    )
                with self:
                    glFramebufferTexture2D(
                        GL_FRAMEBUFFER,
                        texture.attachment_type,
                        GL_TEXTURE_2D,
                        texture.id,
                        0,
                    )
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.attachments:
            return self.attachments[name]  # -- returns the texture

    def resize(self, event):
        for attachment in self.attachments.values():
            attachment.resize(event.size)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.id)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

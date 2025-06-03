from OpenGL.GL import *
from PIL import Image
import numpy as np
from utils.path_resolver import resolve_path

# TODO add debug info


class Texture:
    def __init__(
        self,
        filepath: str = None,
    ):
        self.id = glGenTextures(1)
        self.width = 0
        self.height: int = 0
        self.format: int = GL_RGBA
        self.path: str = filepath

        if filepath:
            self.load_from_file(filepath)

    def load_from_file(
        self,
        filepath: str,
    ):
        self.path = resolve_path(filepath)

        img: Image.Image = Image.open(self.path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # -- flip for opengl coordinates
        img_data: np.ndarray = np.array(img, dtype=np.uint8)

        self.width, self.height = img.size
        channels: int = len(img.getbands())

        self.format = GL_RGBA if channels == 4 else GL_RGB

        with self:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                self.format,
                self.width,
                self.height,
                0,
                self.format,
                GL_UNSIGNED_BYTE,
                img_data,
            )

    def bind(self, unit: int = 0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def delete(self):
        glDeleteTextures(1, [self.id])

    #@classmethod
    #def create_empty(
    #    cls,
    #    width: int,
    #    height: int,
    #    internal_format: int = GL_RGBA,
    #    data_format: int = GL_RGBA,
    #    data_type: int = GL_UNSIGNED_BYTE,
    #    wrap_s: int = GL_CLAMP_TO_EDGE,
    #    wrap_t: int = GL_CLAMP_TO_EDGE,
    #):
    #    tex = cls()
    #    tex.width = width
    #    tex.height = height
    #
    #    with tex:
    #        glTexImage2D(
    #            GL_TEXTURE_2D,
    #            0,
    #            internal_format,
    #            width,
    #            height,
    #            0,
    #            data_format,
    #            data_type,
    #            None,
    #        )
    #        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap_s)
    #        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap_t)
    #        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    #        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    #
    #    return tex
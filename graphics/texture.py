from __future__ import annotations
from OpenGL.GL import *
from pygame.locals import *
from PIL import Image
import numpy as np
from typing import Tuple
from utils.path_resolver import resolve_path


class Texture:
    def __init__(
        self,
        size: Tuple[int, int],
        img_data: np.ndarray = None,
        internal_format=GL_RGBA32F,
        pixel_data_format=GL_RGBA,
        pixel_component_format=GL_FLOAT,
    ):  # -- creates a texture with data (empty if none provided)
        self.id = glGenTextures(1)
        with self:
            glTexImage2D(
                GL_TEXTURE_2D,  # -- texture target
                0,  # -- mipmap level
                internal_format,  # -- internal format
                size[0],  # -- texture width
                size[1],  # -- texture height
                0,  # -- border (must be 0)
                pixel_data_format,  # -- format of pixel data (matches internal format)
                pixel_component_format,  # -- data type of pixel components
                img_data,  # -- pointer to image data
            )

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    @classmethod
    def load_from_file(cls, path: str, *args, **kwargs) -> Texture:
        path = resolve_path(path)
        img: Image.Image = Image.open(path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # -- flip for opengl coordinates
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        img_data: np.ndarray = np.array(img, dtype=np.float32) / 255

        instance = cls(img.size, *args, img_data=img_data, **kwargs)
        return instance

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)
        glActiveTexture(GL_TEXTURE0 + 0)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind_as_image(self, binding: int = 0):
        glBindImageTexture(binding, self.id, 0, GL_FALSE, 0, GL_READ_WRITE, GL_RGBA32F)

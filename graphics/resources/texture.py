from __future__ import annotations
from OpenGL.GL import *
from OpenGL.GL.ARB.bindless_texture import *
from PIL import Image
import numpy as np
from typing import Tuple
from utils.path_resolver import resolve_path
from pathlib import Path


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
        self.size = size
        self.internal_format = internal_format
        self.pixel_data_format = pixel_data_format
        self.pixel_component_format = pixel_component_format
        self._unit = 0
        with self:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            self._set_image_data(img_data)

    def make_bindless(self) -> int:
        handle = glGetTextureHandleARB(self.id)
        glMakeTextureHandleResidentARB(handle)
        return handle

    # -- !!! CLEARS THE TEXTURE !!!
    def resize(self, new_size: Tuple[int, int]) -> Texture:
        self.size = new_size
        self._set_image_data(None)
        return self

    def _set_image_data(self, img_data: np.ndarray = None):
        with self:
            glTexImage2D(
                GL_TEXTURE_2D,  # -- texture target
                0,  # -- mipmap level
                self.internal_format,  # -- internal format
                self.size[0],  # -- texture width
                self.size[1],  # -- texture height
                0,  # -- border (must be 0)
                self.pixel_data_format,  # -- format of pixel data (matches internal format)
                self.pixel_component_format,  # -- data type of pixel components
                img_data,  # -- pointer to image data
            )

    @classmethod
    def as_attachment(cls, attachment_type, *args, **kwargs) -> Texture:
        instance = cls(*args, **kwargs)
        instance.attachment_type = attachment_type
        return instance

    @classmethod
    def load_from_file(cls, path: Path, *args, **kwargs) -> Texture:
        img: Image.Image = Image.open(str(path))
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # -- flip for opengl coordinates

        if img.mode != "RGBA":
            img = img.convert("RGBA")

        img_data: np.ndarray = np.array(img, dtype=np.float32) / 255

        return cls(img.size, *args, img_data=img_data, **kwargs)

    def bind(self):
        glActiveTexture(GL_TEXTURE0 + self._unit)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind_as_image(self, unit: int = 0):
        glBindImageTexture(unit, self.id, 0, GL_FALSE, 0, GL_READ_WRITE, GL_RGBA32F)

    def unit(self, unit: int) -> Texture:
        self._unit = unit
        return self

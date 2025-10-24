from OpenGL.GL import *
from utils.singleton_decorator import singleton
from pathlib import Path
from typing import List, Dict
from graphics.resources.texture import Texture
from utils.path_resolver import resolve_path
from graphics.resources.buffer import Buffer
import numpy as np


@singleton
class TextureLoader:
    def __init__(self):
        # -- asset containers
        self.texture_data: Dict[str, Dict[Texture, int]] = {}
        self.texture_handle_buffer = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.load_textures()

    def __getitem__(self, name: str) -> Dict[Texture, int]:
        return self.texture_data[name]

    def get_texture_data(self, name: str) -> Dict[Texture, int]:
        return self.texture_data[name]

    def load_textures(self):
        texture_paths = list(Path(resolve_path("assets/")).glob("**/*.png"))
        upload_list = []
        for i, path in enumerate(texture_paths):
            texture = Texture.load_from_file(path)
            handle = texture.make_bindless()
            self.texture_data[path.name] = {"texture": texture, "id": i}
            upload_list.append(handle)
        self.texture_handle_buffer.upload_data(np.array(upload_list, dtype=np.uint64))

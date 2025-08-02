from OpenGL.GL import *
from pathlib import Path
from typing import List, Dict
from graphics.resources.texture import Texture
from utils.path_resolver import resolve_path
from graphics.resources.buffer import Buffer
from graphics.resources.shader import Shader
import numpy as np
from utils.debug import debug
from utils.singleton_decorator import singleton


@singleton
class ShaderLoader:
    def __init__(self):
        # -- asset containers
        self.shaders: Dict[str, Shader] = {}
        self.load_shaders()

    def get_shader(self, name: str) -> Shader:
        return self.shaders[name]

    def __getitem__(self, name: str) -> Shader:
        return self.shaders[name]

    def load_shaders(self):

        extension_map = {
            "comp": GL_COMPUTE_SHADER,
            "frag": GL_FRAGMENT_SHADER,
            "vert": GL_VERTEX_SHADER,
        }

        for extension, shader_type in extension_map.items():
            shader_paths = list(Path(resolve_path(".")).glob(f"**/*.{extension}"))
            for path in shader_paths:
                self.shaders[path.name] = Shader(str(path), shader_type)
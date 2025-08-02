from graphics.geometry_renderer import GeometryRenderer
from graphics.geometry_renderer import draw_command_cstruct
from graphics.geometry_renderer import object_data_cstruct
from graphics.loaders.mesh_loader import MeshLoader
from graphics.loaders.texture_loader import TextureLoader

from scene.modules.module_base import Module
from scene.modules.transform import Transform
from OpenGL.GL import *
import glm


class Renderer(Module):
    requires = [Transform]

    def __init_module__(
        self,
        texture: str = "cat_tex.png",
        mesh: str = "cat.obj",
        is_transparent: bool = False,
        is_UI: bool = False,
        is_visible: bool = True,
    ):
        self.mesh_data = MeshLoader[mesh]
        self.texture_data = TextureLoader[texture]

        self.mapped_command_cstruct = draw_command_cstruct.from_address(
            GeometryRenderer.shared_commands.ctypes.data
            + ctypes.sizeof(draw_command_cstruct) * self.parent_obj.id
        )

        self.mapped_data_cstruct = object_data_cstruct.from_address(
            GeometryRenderer.object_data.ctypes.data
            + ctypes.sizeof(object_data_cstruct) * self.parent_obj.id
        )

        # -- properties
        self.is_transparent = is_transparent
        self.is_UI = is_UI
        self.is_visible = is_visible

        self.upload_object_command()
        self.upload_texture_id()

    def deinit(self):
        self.mapped_command_cstruct.instance_count = 0

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        self.mapped_data_cstruct.is_visible = 1 if value else 0
        self._is_visible = value

    @property
    def is_transparent(self):
        return self._is_transparent

    @is_transparent.setter
    def is_transparent(self, value):
        self.mapped_data_cstruct.is_transparent = 1 if value else 0
        self._is_transparent = value

    def upload_model_matrix(self):
        self.mapped_data_cstruct.model = self.parent_obj.transform.model_matrix

    def upload_texture_id(self):
        self.mapped_data_cstruct.texture_id = self.texture_data["id"]

    def upload_object_command(self):
        self.mapped_command_cstruct.count = self.mesh_data["size"]
        self.mapped_command_cstruct.instance_count = 1
        self.mapped_command_cstruct.first_index = self.mesh_data["index_offset"]
        self.mapped_command_cstruct.base_vertex = self.mesh_data["vertex_offset"]
        self.mapped_command_cstruct.base_instance = self.parent_obj.id

from graphics.geometry_renderer import GeometryRenderer
from graphics.geometry_renderer import draw_command_cstruct
from scene.scene import object_data_cstruct, Scene
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

        self.draw_command_mapping = draw_command_cstruct.from_address(
            GeometryRenderer.draw_command_templates.ctypes.data
            + ctypes.sizeof(draw_command_cstruct) * self.parent_obj.id
        )

        self.object_data_mapping = object_data_cstruct.from_address(
            Scene.object_data.ctypes.data + ctypes.sizeof(object_data_cstruct) * self.parent_obj.id
        )

        # -- properties
        self.is_transparent = is_transparent
        self.is_UI = is_UI
        self.is_visible = is_visible

        self.upload_object_command()

        self.mesh_name = mesh
        self.texture_name = texture

        self.mesh = self.mesh_name
        self.texture = self.texture_name

    @property
    def texture(self):
        pass

    @texture.setter
    def texture(self, name):
        self.object_data_mapping.texture_id = TextureLoader[name]["id"]

    @property
    def mesh(self):
        return MeshLoader.get_mesh(self.mesh_name)

    @mesh.setter
    def mesh(self, name):
        self.mesh_data = MeshLoader[name]
        self.draw_command_mapping.count = self.mesh_data["size"]
        self.draw_command_mapping.first_index = self.mesh_data["index_offset"]
        self.draw_command_mapping.base_vertex = self.mesh_data["vertex_offset"]

    def deinit(self):
        self.draw_command_mapping.instance_count = 0
        self.object_data_mapping.is_visible = 0

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        self.object_data_mapping.is_visible = 1 if value else 0
        self._is_visible = value

    @property
    def is_transparent(self):
        return self._is_transparent

    @is_transparent.setter
    def is_transparent(self, value):
        self.object_data_mapping.is_transparent = 1 if value else 0
        self._is_transparent = value

    def upload_object_command(self):
        self.draw_command_mapping.instance_count = 1
        self.draw_command_mapping.base_instance = self.parent_obj.id

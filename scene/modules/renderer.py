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

        # -- arrays mapped to gpu buffers
        self.gpu_draw_commands = GeometryRenderer.draw_commands
        self.gpu_object_data = GeometryRenderer.object_data

        # -- properties
        self.is_transparent = is_transparent
        self.is_UI = is_UI
        self.is_visible = is_visible

        # -- resources
        self.texture = texture

        self.upload_draw_command()
        self.upload_texture_id()

    def upload_model_matrix(self):
        ctypes.memmove(
            self.gpu_object_data.ctypes.data
            + ctypes.sizeof(object_data_cstruct) * self.parent_obj.id,
            glm.value_ptr(self.parent_obj.transform.model_matrix),
            glm.sizeof(self.parent_obj.transform.model_matrix),
        )

    def upload_texture_id(self):
        self.gpu_object_data[self.parent_obj.id]["texture_id"] = self.texture_data["id"]

    def upload_draw_command(self):
        command = draw_command_cstruct(
            count=self.mesh_data["size"],
            instance_count=1 if self.is_visible else 0,
            first_index=self.mesh_data["index_offset"],
            base_vertex=self.mesh_data["vertex_offset"],
            base_instance=self.parent_obj.id,
        )
        command.assign_to_element(self.gpu_draw_commands, self.parent_obj.id)

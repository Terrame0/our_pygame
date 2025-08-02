from __future__ import annotations
from typing import List, Dict, Any
from graphics.resources.framebuffer import Framebuffer
from utils.debug import debug
from utils.singleton_decorator import singleton

from pyglm import glm
import numpy as np
from OpenGL.GL import *

from graphics.resources.ctypes_struct import create_struct
from graphics.resources.buffer import Buffer
from graphics.resources.shader import Shader
from graphics.resources.shader_program import ShaderProgram
from graphics.loaders.mesh_loader import MeshLoader
from graphics.loaders.texture_loader import TextureLoader
from graphics.loaders.shader_loader import ShaderLoader
from graphics.resources.texture import Texture
from graphics.window import Window

from scene.scene import Scene


# -- command data for MDI
draw_command_cstruct = create_struct(
    count=glm.uvec1,
    instance_count=glm.uvec1,
    first_index=glm.uvec1,
    base_vertex=glm.uvec1,
    base_instance=glm.uvec1,
)

# -- per object data
object_data_cstruct = create_struct(
    model=glm.mat4,
    texture_id=glm.uvec1,
    is_visible=glm.uvec1,
    is_transparent=glm.uvec1,
)


@singleton
class GeometryRenderer:

    def __init__(self):
        self.init_buffers()
        self.init_shaders()
        self.init_framebuffer()

    def init_framebuffer(self):
        self.geometry_fbo = Framebuffer(
            accumulation_attachment=Texture.as_attachment(
                size=Window.size,
                attachment_type=GL_COLOR_ATTACHMENT0,
            ),
            revealage_attachment=Texture.as_attachment(
                size=Window.size,
                attachment_type=GL_COLOR_ATTACHMENT1,
                internal_format=GL_R32F,
                pixel_data_format=GL_RED,
            ),
            color_attachment=Texture.as_attachment(
                size=Window.size,
                attachment_type=GL_COLOR_ATTACHMENT2,
            ),
            depth_attachment=Texture.as_attachment(
                size=Window.size,
                attachment_type=GL_DEPTH_ATTACHMENT,
                internal_format=GL_DEPTH_COMPONENT32,
                pixel_data_format=GL_DEPTH_COMPONENT,
            ),
        )

    def init_buffers(self):

        # -- atomic counter to keep track of the number of opaque objects to render
        self.opaque_counter_buffer = Buffer(GL_ATOMIC_COUNTER_BUFFER)
        self.opaque_counter_buffer.upload_data(np.array(0, dtype=np.uint32))
        self.opaque_counter = self.opaque_counter_buffer.map_to_array()

        # -- same as above but for transparent objects
        self.transparent_counter_buffer = Buffer(GL_ATOMIC_COUNTER_BUFFER)
        self.transparent_counter_buffer.upload_data(np.array(0, dtype=np.uint32))
        self.transparent_counter = self.transparent_counter_buffer.map_to_array()

        # -- initial value array
        empty_commands = np.zeros(Scene.MAX_OBJECTS, dtype=draw_command_cstruct)

        # -- command buffers that the culling shader writes commands to every frame
        # -- they are the ones that get used in the drawing passes
        self.transparent_command_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.transparent_command_buffer.upload_data(empty_commands)
        self.opaque_command_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.opaque_command_buffer.upload_data(empty_commands)

        # TODO migrate this data into the object_data_buffer
        # -- a command buffer that the culling shader copies commands from
        # -- objects write their commands to this buffer
        self.shared_command_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.shared_command_buffer.upload_data(empty_commands)

        # -- command buffer mapped to an array (used in the objects)
        self.shared_commands = self.shared_command_buffer.map_to_array()

        # -- initial value array
        empty_object_data = np.zeros(Scene.MAX_OBJECTS, dtype=object_data_cstruct)

        # -- a buffer for per-object data that is used in the shaders
        self.object_data_buffer = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.object_data_buffer.upload_data(empty_object_data)
        self.object_data = self.object_data_buffer.map_to_array()

    def init_shaders(self):
        self.culling_shader = ShaderProgram(
            "culler.comp",
        )

        self.geometry_shader = ShaderProgram(
            "geometry.frag",
            "geometry.vert",
        )
        self.outline_shader = ShaderProgram(
            "outline.frag",
            "outline.vert",
        )

    def reset_object_counters(self):
        pass

    def draw(self) -> Framebuffer:
        # -- culling and separating objects' commands
        self.opaque_counter[0] = 0
        self.transparent_counter[0] = 0

        self.opaque_counter_buffer.bind_base(0, GL_ATOMIC_COUNTER_BUFFER)
        self.transparent_counter_buffer.bind_base(1, GL_ATOMIC_COUNTER_BUFFER)

        self.object_data_buffer.bind_base(0, GL_SHADER_STORAGE_BUFFER)
        self.shared_command_buffer.bind_base(1, GL_SHADER_STORAGE_BUFFER)
        self.opaque_command_buffer.bind_base(2, GL_SHADER_STORAGE_BUFFER)
        self.transparent_command_buffer.bind_base(3, GL_SHADER_STORAGE_BUFFER)

        with self.culling_shader:
            glDispatchCompute(Scene.MAX_OBJECTS // 256 + 1, 1, 1)

        # print(self.opaque_counter_buffer.get_data())
        # print(self.transparent_counter_buffer.get_data())
        # 
        # print(self.shared_commands)
        # print(self.opaque_command_buffer.get_data())
        # print(self.transparent_command_buffer.get_data())

        # -- preparing to render
        self.object_data_buffer.bind_base(0, GL_SHADER_STORAGE_BUFFER)  # -- per object data ssbo
        TextureLoader.texture_handle_buffer.bind_base(
            1, GL_SHADER_STORAGE_BUFFER
        )  # -- per object texture handles
        Scene.camera.camera_ubo.bind_base(0, GL_UNIFORM_BUFFER)  # -- camera ubo
        glBindVertexArray(MeshLoader.joint_vao)

        self.opaque_pass()
        self.transparent_pass()

        return self.geometry_fbo

    def opaque_pass(self):
        pass

    def transparent_pass(self):

        with self.transparent_command_buffer, self.geometry_fbo:
            glClearBufferfv(GL_COLOR, 0, (0, 0, 0, 0))
            glClearBufferfv(GL_COLOR, 1, (1, 0, 0, 0))
            glClearBufferfv(GL_COLOR, 2, (0, 0, 0, 0))
            glDepthMask(GL_TRUE)
            glClearBufferfv(GL_DEPTH, 0, 1)  # -- depth mask must be enabled for this to work
            glDepthMask(GL_FALSE)
            glEnable(GL_BLEND)

            glBlendFunci(0, GL_ONE, GL_ONE)
            glBlendFunci(1, GL_ZERO, GL_ONE_MINUS_SRC_COLOR)
            glBlendFunci(2, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2])
            glDisable(GL_CULL_FACE)

            with self.geometry_shader:
                glMultiDrawElementsIndirect(
                    GL_TRIANGLES,
                    GL_UNSIGNED_INT,
                    None,
                    Scene.MAX_OBJECTS,
                    0,
                )

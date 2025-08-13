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
        self.transparent_draw_command_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.transparent_draw_command_buffer.upload_data(empty_commands)
        self.opaque_draw_command_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.opaque_draw_command_buffer.upload_data(empty_commands)

        # -- a command buffer that the culling shader copies commands from
        # -- objects write their commands to this buffer
        self.draw_command_template_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.draw_command_template_buffer.upload_data(empty_commands)

        # -- command buffer mapped to an array (used in the objects)
        self.draw_command_templates = self.draw_command_template_buffer.map_to_array()

    def init_shaders(self):
        self.culling_shader = ShaderProgram(
            "culler.comp",
        )

        self.transparent_shader = ShaderProgram(
            "transparent.frag",
            "geometry.vert",
        )

        self.opaque_shader = ShaderProgram(
            "opaque.frag",
            "geometry.vert",
        )

        self.outline_shader = ShaderProgram(
            "outline.frag",
            "geometry.vert",
        )

    def draw(self) -> Framebuffer:
        # -- culling and separating objects' commands
        self.opaque_counter[0] = 0
        self.transparent_counter[0] = 0

        self.opaque_counter_buffer.bind_base(0, GL_ATOMIC_COUNTER_BUFFER)
        self.transparent_counter_buffer.bind_base(1, GL_ATOMIC_COUNTER_BUFFER)

        Scene.object_data_buffer.bind_base(0, GL_SHADER_STORAGE_BUFFER)
        self.draw_command_template_buffer.bind_base(1, GL_SHADER_STORAGE_BUFFER)
        self.opaque_draw_command_buffer.bind_base(2, GL_SHADER_STORAGE_BUFFER)
        self.transparent_draw_command_buffer.bind_base(3, GL_SHADER_STORAGE_BUFFER)

        with self.culling_shader:
            glDispatchCompute(Scene.MAX_OBJECTS // 256 + 1, 1, 1)

        # -- preparing to render

        # -- binding per object data ssbo
        Scene.object_data_buffer.bind_base(0, GL_SHADER_STORAGE_BUFFER)

        # -- binding per object texture handle buffer
        TextureLoader.texture_handle_buffer.bind_base(1, GL_SHADER_STORAGE_BUFFER)

        # -- binding camera ubo
        Scene.camera.camera_ubo.bind_base(0, GL_UNIFORM_BUFFER)

        # -- binding joint vao
        glBindVertexArray(MeshLoader.joint_vao)

        with self.geometry_fbo:
            glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2])
            glClearBufferfv(GL_COLOR, 0, (0, 0, 0, 0))

            # -- clearing depth attachment
            glDepthMask(GL_TRUE)  # -- depth mask must be enabled for it to work
            glClearBufferfv(GL_DEPTH, 0, 1)
            glClearBufferfv(GL_COLOR, 0, (0, 0, 0, 0))
            glClearBufferfv(GL_COLOR, 1, (1, 0, 0, 0))
            glClearBufferfv(GL_COLOR, 2, (0, 0, 0, 0))

        self.opaque_pass()
        self.transparent_pass()

        return self.geometry_fbo

    def opaque_pass(self):
        with self.opaque_draw_command_buffer, self.geometry_fbo:

            # -- enabling backface culling
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)

            # -- enabling writes to the depth buffer
            glDepthMask(GL_TRUE)

            # -- disabling blending
            glEnable(GL_BLEND)
            glBlendFunci(2, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            with self.opaque_shader:
                glMultiDrawElementsIndirect(
                    GL_TRIANGLES,
                    GL_UNSIGNED_INT,
                    None,
                    self.opaque_counter_buffer.get_data()[0],
                    0,
                )

            glPolygonMode(GL_BACK, GL_LINE)
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)

            with self.outline_shader:
                glMultiDrawElementsIndirect(
                    GL_TRIANGLES,
                    GL_UNSIGNED_INT,
                    None,
                    self.opaque_counter_buffer.get_data()[0],
                    0,
                )

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def transparent_pass(self):
        with self.transparent_draw_command_buffer, self.geometry_fbo:

            # -- disabling backface culling
            glDisable(GL_CULL_FACE)

            # -- disabling writes to the depth buffer
            glDepthMask(GL_FALSE)

            # -- enabling blending
            glEnable(GL_BLEND)
            glBlendFunci(0, GL_ONE, GL_ONE)
            glBlendFunci(1, GL_ZERO, GL_ONE_MINUS_SRC_COLOR)

            # -- drawing transparent objects
            with self.transparent_shader:
                glMultiDrawElementsIndirect(
                    GL_TRIANGLES,
                    GL_UNSIGNED_INT,
                    None,
                    self.transparent_counter_buffer.get_data()[0],
                    0,
                )

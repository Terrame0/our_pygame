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
    count=glm.uint32,
    instance_count=glm.uint32,
    first_index=glm.uint32,
    base_vertex=glm.uint32,
    base_instance=glm.uint32,
)

# -- per object data
object_data_cstruct = create_struct(
    model=glm.mat4,
    texture_id=glm.uint32,
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
        self.opaque_object_counter = Buffer(GL_ATOMIC_COUNTER_BUFFER)
        self.opaque_object_counter.upload_data(
            np.array(0, dtype=np.uint32),
        )

        # -- a buffer for drawing commands that glDrawElementsInstanced uses
        self.draw_commands = np.zeros(Scene.MAX_OBJECTS, dtype=draw_command_cstruct)
        self.draw_command_buffer = Buffer(GL_DRAW_INDIRECT_BUFFER)
        self.draw_command_buffer.upload_data(self.draw_commands)
        self.draw_commands = self.draw_command_buffer.map_to_array()

        # -- a buffer for per-object data that is used in the shaders
        self.object_data = np.zeros(Scene.MAX_OBJECTS, dtype=object_data_cstruct)
        self.object_data_buffer = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.object_data_buffer.upload_data(self.object_data)
        self.object_data = self.object_data_buffer.map_to_array()

    def init_shaders(self):
        self.geometry_shader = ShaderProgram(
            "geometry.frag",
            "geometry.vert",
        )
        self.outline_shader = ShaderProgram(
            "outline.frag",
            "outline.vert",
        )

    def opaque_pass(self):
        pass

    def transparent_pass(self):
        pass

    def draw(self) -> Framebuffer:
        self.object_data_buffer.bind_base(0, GL_SHADER_STORAGE_BUFFER)  # -- per object data ssbo
        TextureLoader.texture_handle_buffer.bind_base(
            1, GL_SHADER_STORAGE_BUFFER
        )  # -- per object texture handles
        Scene.camera.camera_ubo.bind_base(0, GL_UNIFORM_BUFFER)  # -- camera ubo
        glBindVertexArray(MeshLoader.joint_vao)
        with self.draw_command_buffer, self.geometry_fbo:
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

            # glDepthMask(GL_TRUE)
            # glBlendFunc(GL_ONE, GL_ZERO)
            # glEnable(GL_CULL_FACE)
            # glCullFace(GL_FRONT)
            # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            # with self.outline_shader:
            #    glMultiDrawElementsIndirect(
            #        GL_TRIANGLES,
            #        GL_UNSIGNED_INT,
            #        None,
            #        Scene.MAX_OBJECTS,
            #        0,
            #    )
            # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            # glCullFace(GL_BACK)

        return self.geometry_fbo
from OpenGL.GL import *
from utils.singleton_decorator import singleton
from graphics.resources.shader import Shader
from graphics.resources.shader_program import ShaderProgram
from scene.scene import Scene
from pyglm import glm
from graphics.resources.texture import Texture
from core.clock import Clock
from graphics.resources.framebuffer import Framebuffer
from graphics.resources.buffer import Buffer
from graphics.window import Window
import numpy as np


@singleton
class RenderpassIDManager:
    MAX_RENDERPASS_COUNT = 1000

    def __init__(self):
        self.id_queue_pointer = self.MAX_RENDERPASS_COUNT - 1
        self.id_queue = [x for x in range(self.MAX_RENDERPASS_COUNT)]

    def get_id(self):
        if self.id_queue_pointer < 0:
            raise RuntimeError(
                f"(!) renderpass ID pool exhausted!"
            )  # -- i hope there can't be more than a thousand renderpasses :)
        out = self.id_queue[self.id_queue_pointer]
        self.id_queue[self.id_queue_pointer] = 0
        self.id_queue_pointer -= 1
        return out

    def return_id(self, idx: int):
        self.id_queue_pointer += 1
        self.id_queue[self.id_queue_pointer] = idx


@singleton
class ParticleSystem:
    MAX_PARTICLES = 1000

    @property
    def active_particles(self):
        return self.MAX_PARTICLES - self.dead_particles_stack_pointer.get_data()[0]

    def setup_particle_fbo(self):
        # -- fbo that particles will be rendered to
        self.particle_fbo = Framebuffer(
            color_attachment=Texture.as_attachment(
                size=Window.size,
                attachment_type=GL_COLOR_ATTACHMENT0,
            ),
            depth_attachment=Texture.as_attachment(
                size=Window.size,
                attachment_type=GL_DEPTH_ATTACHMENT,
                internal_format=GL_DEPTH_COMPONENT32,
                pixel_data_format=GL_DEPTH_COMPONENT,
                pixel_component_format=GL_FLOAT,
            ),
        )

    def create_shader_programs(self):
        self.particle_updater = ShaderProgram(
            "particle_updater.comp",
        )

    def create_default_quad_vao(self):
        # -- a quad to do instanced rendering with
        quad_vertices = np.array(
            [
                # vertex 0: bottom-left
                -1.0,
                -1.0,
                0.0,
                # vertex 1: bottom-right
                1.0,
                -1.0,
                0.0,
                # vertex 2: top-left
                -1.0,
                1.0,
                0.0,
                # vertex 3: top-right
                1.0,
                1.0,
                0.0,
            ],
            dtype=np.float32,
        )

        quad_indices = np.array([0, 1, 2, 1, 3, 2], dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # -- vertex buffer
        vbo = Buffer(GL_ARRAY_BUFFER)
        vbo.upload_data(quad_vertices)

        # -- element buffer
        ebo = Buffer(GL_ELEMENT_ARRAY_BUFFER)
        ebo.upload_data(quad_indices)

        # -- vertex attributes
        with vbo, ebo:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)
            glEnableVertexAttribArray(0)
            glBindVertexArray(0)

    def create_particle_state_buffers(self):
        self.dead_particles_stack = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.dead_particles_stack.upload_data(
            np.array(range(0, self.MAX_PARTICLES), dtype=np.uint32),
        )

        self.dead_particles_stack_pointer = Buffer(GL_ATOMIC_COUNTER_BUFFER)
        self.dead_particles_stack_pointer.upload_data(
            np.array(self.MAX_PARTICLES, dtype=np.uint32),
        )

    def create_particle_attribute_buffers(self):
        self.particle_positions = Buffer(GL_ARRAY_BUFFER)
        self.particle_positions.upload_data(
            np.array([0.0] * 4 * self.MAX_PARTICLES, dtype=np.float32),
        )

        self.particle_velocities = Buffer(GL_ARRAY_BUFFER)
        self.particle_velocities.upload_data(
            np.array([0.0] * 4 * self.MAX_PARTICLES, dtype=np.float32),
        )

        self.particle_lifetimes = Buffer(GL_ARRAY_BUFFER)
        self.particle_lifetimes.upload_data(
            np.array([0.0] * self.MAX_PARTICLES, dtype=np.float32),
        )

        self.renderpass_id_buffer = Buffer(GL_ARRAY_BUFFER)
        self.renderpass_id_buffer.upload_data(
            np.array([0.0] * self.MAX_PARTICLES, dtype=np.uint32),
        )

        with self.particle_positions:
            glBindVertexArray(self.vao)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
            glVertexAttribDivisor(1, 1)
            glEnableVertexAttribArray(1)
            glBindVertexArray(0)

        with self.particle_velocities:
            glBindVertexArray(self.vao)
            glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 0, None)
            glVertexAttribDivisor(2, 1)
            glEnableVertexAttribArray(2)
            glBindVertexArray(0)

        with self.particle_lifetimes:
            glBindVertexArray(self.vao)
            glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 0, None)
            glVertexAttribDivisor(3, 1)
            glEnableVertexAttribArray(3)
            glBindVertexArray(0)

    def __init__(self):
        self.create_shader_programs()
        self.setup_particle_fbo()
        self.create_default_quad_vao()
        self.create_particle_state_buffers()
        self.create_particle_attribute_buffers()

    def bind_spawn_vars(self, program: ShaderProgram, renderpass_id: int):
        self.dead_particles_stack_pointer.bind_base(0, GL_ATOMIC_COUNTER_BUFFER)
        glUniform1ui(
            program.get_uniform_id("current_renderpass"),
            renderpass_id,
        )
        self.dead_particles_stack.bind_base(
            program.get_ssbo_id("dead_particles_stack"), GL_SHADER_STORAGE_BUFFER
        )
        self.particle_positions.bind_base(
            program.get_ssbo_id("particle_positions"), GL_SHADER_STORAGE_BUFFER
        )
        self.particle_velocities.bind_base(
            program.get_ssbo_id("particle_velocities"), GL_SHADER_STORAGE_BUFFER
        )
        self.particle_lifetimes.bind_base(
            program.get_ssbo_id("particle_lifetimes"), GL_SHADER_STORAGE_BUFFER
        )
        self.renderpass_id_buffer.bind_base(
            program.get_ssbo_id("particle_renderpass_ids"), GL_SHADER_STORAGE_BUFFER
        )

    def bind_render_vars(self, program: ShaderProgram, renderpass_id: int):
        glEnable(GL_DEPTH_TEST)
        self.renderpass_id_buffer.bind_base(
            program.get_ssbo_id("particle_renderpass_ids"), GL_SHADER_STORAGE_BUFFER
        )
        glUniformMatrix4fv(
            program.get_uniform_id("projection"),
            1,
            False,
            glm.value_ptr(Scene.camera.projection_matrix),
        )
        glUniformMatrix4fv(
            program.get_uniform_id("view"),
            1,
            False,
            glm.value_ptr(Scene.camera.view_matrix),
        )
        glUniformMatrix4fv(
            program.get_uniform_id("model"),
            1,
            False,
            glm.value_ptr(Scene.camera_object.transform.R),
        )
        glUniform1ui(
            program.get_uniform_id("current_renderpass"),
            renderpass_id,
        )

    # -- is called after rendering
    def reset_particles(self):
        with self.particle_fbo:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        with self.particle_updater:
            glUniform1f(0, Clock.delta_time)
            self.dead_particles_stack_pointer.bind_base(0, GL_ATOMIC_COUNTER_BUFFER)
            self.dead_particles_stack.bind_base(0, GL_SHADER_STORAGE_BUFFER)
            self.particle_positions.bind_base(1, GL_SHADER_STORAGE_BUFFER)
            self.particle_velocities.bind_base(2, GL_SHADER_STORAGE_BUFFER)
            self.particle_lifetimes.bind_base(3, GL_SHADER_STORAGE_BUFFER)
            # -- updating all the particles because they may be instantiated out of order (i have no idea how to change that)
            glDispatchCompute(self.MAX_PARTICLES // 64 + 1, 1, 1)

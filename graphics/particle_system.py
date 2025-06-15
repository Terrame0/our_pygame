import random
import pygame
from utils import custom_events
from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from scene.scene import Scene
from utils.debug import debug
from pyglm import glm
from graphics.texture import Texture
from core.clock import Clock
from core.event_manager import EventManager
from graphics.framebuffer import Framebuffer
from graphics.buffer import Buffer


@singleton
class ParticleSystem:
    MAX_PARTICLES = 100000

    def setup_fbo(self):
        self.fbo = Framebuffer()
        with self.fbo:
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_2D,
                self.result_texture.id,
                0,
            )
            depth_texture = Texture(
                (800, 600),
                internal_format=GL_DEPTH_COMPONENT32,
                pixel_data_format=GL_DEPTH_COMPONENT,
                pixel_component_format=GL_FLOAT,
            )
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_DEPTH_ATTACHMENT,
                GL_TEXTURE_2D,
                depth_texture.id,
                0,
            )

    def create_shader_programs(self):
        self.spawner_program = ShaderProgram(
            Shader(
                "graphics/shaders/particle_system/particle_spawner.comp",
                GL_COMPUTE_SHADER,
            )
        )

        self.creator_program = ShaderProgram(
            Shader(
                "graphics/shaders/particle_system/particle_updater.comp",
                GL_COMPUTE_SHADER,
            )
        )

        # -- shader program that renders particles
        self.renderer_program = ShaderProgram(
            Shader(
                "graphics/shaders/particle_system/particle_renderer.frag",
                GL_FRAGMENT_SHADER,
            ),
            Shader(
                "graphics/shaders/particle_system/particle_renderer.vert",
                GL_VERTEX_SHADER,
            ),
        )

    def create_default_quad_vao(self):
        # -- a quad to do instanced rendering with
        quad_vertices = (
            glm.array(
                glm.float32,
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
            )
            * 0.2
        )

        quad_indices = glm.array(glm.uint32, *[0, 1, 2, 1, 3, 2])

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # -- vertex buffer
        vbo = Buffer(GL_ARRAY_BUFFER)
        vbo.upload_data(quad_vertices, usage=GL_STATIC_DRAW)

        # -- element buffer
        ebo = Buffer(GL_ELEMENT_ARRAY_BUFFER)
        ebo.upload_data(quad_indices, usage=GL_STATIC_DRAW)

        # -- vertex attributes
        with vbo, ebo:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)
            glEnableVertexAttribArray(0)
            glBindVertexArray(0)

    def create_particle_state_buffers(self):
        self.dead_particles_stack = Buffer(GL_SHADER_STORAGE_BUFFER)
        self.dead_particles_stack.upload_data(
            glm.array(glm.uint32, *range(0, self.MAX_PARTICLES)), GL_DYNAMIC_DRAW
        )

        self.dead_particles_stack_pointer = Buffer(GL_ATOMIC_COUNTER_BUFFER)
        self.dead_particles_stack_pointer.upload_data(
            glm.array(glm.uint32, self.MAX_PARTICLES, GL_DYNAMIC_DRAW)
        )

    def create_particle_attribute_buffers(self):
        self.particle_positions = Buffer(GL_ARRAY_BUFFER)
        self.particle_positions.upload_data(
            glm.array([glm.vec4(0)] * self.MAX_PARTICLES),
            GL_DYNAMIC_DRAW,
        )

        self.particle_velocities = Buffer(GL_ARRAY_BUFFER)
        self.particle_velocities.upload_data(
            glm.array([glm.vec4(0)] * self.MAX_PARTICLES),
            GL_DYNAMIC_DRAW,
        )

        self.particle_lifetimes = Buffer(GL_ARRAY_BUFFER)
        self.particle_lifetimes.upload_data(
            glm.array(glm.float32, *([0] * self.MAX_PARTICLES)),
            GL_DYNAMIC_DRAW,
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
        self.result_texture = Texture((800, 600))
        self.create_shader_programs()
        self.setup_fbo()
        self.create_default_quad_vao()
        self.create_particle_attribute_buffers()
        self.create_particle_state_buffers()

        EventManager().subscribe(custom_events.UPDATE, self.create_particles)

    def create_particles(self):
        with self.spawner_program:
            glUniform1ui(0, 1)
            glUniform4fv(
                1,
                1,
                glm.value_ptr(
                    (
                        glm.vec4(random.random(), random.random(), random.random(), 1)
                        - 0.5
                    )
                    * 100
                ),
            )
            self.dead_particles_stack_pointer.bind_base(0, GL_ATOMIC_COUNTER_BUFFER)
            self.dead_particles_stack.bind_base(0, GL_SHADER_STORAGE_BUFFER)
            self.particle_positions.bind_base(1, GL_SHADER_STORAGE_BUFFER)
            self.particle_velocities.bind_base(2, GL_SHADER_STORAGE_BUFFER)
            self.particle_lifetimes.bind_base(3, GL_SHADER_STORAGE_BUFFER)
            glDispatchCompute(self.MAX_PARTICLES // 64 + 1, 1, 1)

    def render_particles(self, target_fbo: Framebuffer):

        # -- update particles
        with self.creator_program:
            glUniform1f(0, Clock().delta_time)
            self.dead_particles_stack_pointer.bind_base(0, GL_ATOMIC_COUNTER_BUFFER)
            self.dead_particles_stack.bind_base(0, GL_SHADER_STORAGE_BUFFER)
            self.particle_positions.bind_base(1, GL_SHADER_STORAGE_BUFFER)
            self.particle_velocities.bind_base(2, GL_SHADER_STORAGE_BUFFER)
            self.particle_lifetimes.bind_base(3, GL_SHADER_STORAGE_BUFFER)
            glDispatchCompute(self.MAX_PARTICLES // 64 + 1, 1, 1)

        # -- render particles
        with target_fbo, self.renderer_program:

            self.dead_particles_stack.bind_base(0, GL_SHADER_STORAGE_BUFFER)

            glEnable(GL_DEPTH_TEST)
            glUniformMatrix4fv(
                0, 1, False, glm.value_ptr(Scene().camera.projection_matrix)
            )
            glUniformMatrix4fv(1, 1, False, glm.value_ptr(Scene().camera.view_matrix))
            glUniformMatrix4fv(
                2, 1, False, glm.value_ptr(Scene().camera_object.transform.R)
            )
            glBindVertexArray(self.vao)
            glDrawElementsInstanced(
                GL_TRIANGLES, 6, GL_UNSIGNED_INT, None, self.MAX_PARTICLES
            )

        # target.bind_as_image(binding=0)
        # self.result_texture.bind_as_image(binding=1)
        #
        # with self.compute_program, depth:
        #    glUniformMatrix4fv(
        #        0, 1, False, glm.value_ptr(Scene().camera.projection_matrix)
        #    )
        #    glUniformMatrix4fv(1, 1, False, glm.value_ptr(Scene().camera.view_matrix))
        #    glUniform1f(2, Scene().camera.near_plane)
        #    glUniform1f(3, Scene().camera.far_plane)
        #    glDispatchCompute(800 // 16 + 1, 600 // 16 + 1, 1)

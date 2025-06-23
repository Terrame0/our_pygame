import random
from utils import custom_events
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module
from graphics.shader import Shader
from graphics.shader_program import ShaderProgram
from OpenGL.GL import *
from graphics.particle_system import ParticleSystem
from graphics.particle_system import RenderpassManager


class SpeedLinesEmitter(Module):

    def __init_module__(self, player: SceneObject):
        self.player = player
        self.renderpass_id = RenderpassManager().get_renderpass_id()
        print(self.renderpass_id)

        # -- shader program that spawns particles
        self.spawner_program = ShaderProgram(
            Shader(
                "graphics/shaders/particle_system/speed_lines/speed_line_spawner.comp",
                GL_COMPUTE_SHADER,
            )
        )

        # -- shader program that renders particles
        self.renderer_program = ShaderProgram(
            Shader(
                "graphics/shaders/particle_system/speed_lines/speed_line_renderer.frag",
                GL_FRAGMENT_SHADER,
            ),
            Shader(
                "graphics/shaders/particle_system/speed_lines/speed_line_renderer.vert",
                GL_VERTEX_SHADER,
            ),
        )

        self.subscribe_to_event(custom_events.UPDATE, self.render_particles)

    def deinit(self):
        RenderpassManager().return_renderpass_id(self.renderpass_id)

    def render_particles(self):
        # -- spawn particles
        with self.spawner_program:
            ParticleSystem().bind_spawn_vars(self.spawner_program, self.renderpass_id)
            glUniform4fv(
                self.spawner_program.get_uniform_id("offset"),
                1,
                glm.value_ptr(
                    (
                        glm.vec4(random.random(), random.random(), random.random(), 1)
                        - 0.5
                    )
                    * 5
                ),
            )
            glUniform4fv(
                self.spawner_program.get_uniform_id("player_position"),
                1,
                glm.value_ptr(self.player.transform.position),
            )
            glUniform4fv(
                self.spawner_program.get_uniform_id("player_velocity"),
                1,
                glm.value_ptr(self.player.physics_body.velocity),
            )
            glDispatchCompute(ParticleSystem().MAX_PARTICLES // 64 + 1, 1, 1)

        # -- render particles
        with ParticleSystem().particle_fbo, self.renderer_program:

            ParticleSystem().bind_render_vars(self.renderer_program, self.renderpass_id)

            glUniform4fv(
                self.renderer_program.get_uniform_id("player_velocity"),
                1,
                glm.value_ptr(self.player.physics_body.velocity),
            )

            glBindVertexArray(ParticleSystem().vao)
            glDrawElementsInstanced(
                GL_TRIANGLES, 6, GL_UNSIGNED_INT, None, ParticleSystem().MAX_PARTICLES
            )
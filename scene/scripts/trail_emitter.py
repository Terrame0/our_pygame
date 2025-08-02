import random
from utils import custom_events
from pyglm import glm
from scene.modules.module_base import Module
from graphics.resources.shader import Shader
from graphics.resources.shader_program import ShaderProgram
from OpenGL.GL import *
from graphics.particle_system import ParticleSystem
from graphics.particle_system import RenderpassIDManager
from utils.singleton_decorator import singleton


@singleton
class _TrailEmitterShaders:
    def __init__(self):
        # -- shader program that spawns particles
        self.spawner_program = ShaderProgram(
            "trail_spawner.comp",
        )

        # -- shader program that renders particles
        self.renderer_program = ShaderProgram(
            "trail_renderer.frag",
            "trail_renderer.vert",
        )


class TrailEmitter(Module):

    def __init_module__(self, trail_color: glm.vec3 = glm.vec3(1, 1, 1)):
        self.renderpass_id = RenderpassIDManager.get_id()
        self.trail_color = trail_color
        self.is_emitting = False

        self.spawner_program = _TrailEmitterShaders.spawner_program
        self.renderer_program = _TrailEmitterShaders.renderer_program

        self.subscribe_to_event(custom_events.UPDATE, self.render_particles)

    def deinit(self):
        RenderpassIDManager.return_id(self.renderpass_id)

    def render_particles(self):
        if self.is_emitting:
            # -- spawn particles
            with self.spawner_program:
                ParticleSystem.bind_spawn_vars(self.spawner_program, self.renderpass_id)
                glUniform4fv(
                    self.spawner_program.get_uniform_id("offset"),
                    1,
                    glm.value_ptr(
                        (glm.vec4(random.random(), random.random(), random.random(), 1) - 0.5)
                        * 2
                        * 0.7
                    ),
                )
                glUniform4fv(
                    self.spawner_program.get_uniform_id("projectile_position"),
                    1,
                    glm.value_ptr(self.parent_obj.transform.position),
                )
                glUniform1ui(
                    self.spawner_program.get_uniform_id("particle_count"),
                    1,
                )
                glDispatchCompute(ParticleSystem.MAX_PARTICLES // 64 + 1, 1, 1)

        # -- render particles
        with ParticleSystem.particle_fbo, self.renderer_program:
            ParticleSystem.bind_render_vars(self.renderer_program, self.renderpass_id)
            glUniform3fv(
                self.renderer_program.get_uniform_id("trail_color"),
                1,
                glm.value_ptr(self.trail_color),
            )
            glBindVertexArray(ParticleSystem.vao)
            glDrawElementsInstanced(
                GL_TRIANGLES, 6, GL_UNSIGNED_INT, None, ParticleSystem.MAX_PARTICLES
            )

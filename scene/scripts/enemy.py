from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.physics_body import PhysicsBody
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module
from core.clock import Clock
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.projectile import Projectile
from graphics.resources.texture import Texture
from scene.scripts.health import Health
from scene.scripts.trail_emitter import TrailEmitter
from core.game_manager import GameManager
import pygame
from utils.path_resolver import resolve_path


class Enemy(Module):
    requires = [Transform, Renderer, PhysicsBody, Health]

    def __init_module__(self, player: SceneObject):
        self.shoot_sound = pygame.mixer.Sound(resolve_path("assets/sounds/shoot.mp3"))
        self.hit_sound = pygame.mixer.Sound(resolve_path("assets/sounds/hit.mp3"))

        self.player = player
        self.target_vector = None
        self.last_shot = Clock.now
        self.reload_time = 3
        self.subscribe_to_event(custom_events.UPDATE, self.check_health)
        # self.subscribe_to_event(custom_events.UPDATE, self.update_heading)
        # self.subscribe_to_event(custom_events.UPDATE, self.shoot)

    def deinit(self):
        GameManager.enemies_alive -= 1

    def shoot(self):
        if Clock.now - self.last_shot > self.reload_time:
            self.shoot_sound.set_volume(
                1
                / glm.distance(self.player.transform.position, self.parent_obj.transform.position)
                * 10
            )
            self.shoot_sound.play()
            self.last_shot = Clock.now
            projectile = SceneObject(
                name="projectile",
                modules=[
                    Transform(),
                    Mesh(path="assets/meshes/plane.obj"),
                    PhysicsBody(collision_radius=0.3),
                    Renderer(texture=Texture.load_from_file("assets/textures/plasma_red.png")),
                    Projectile(
                        progenitor=self.parent_obj,
                        parent_velocity=self.parent_obj.physics_body.velocity,
                        exclude_from_collision=[self.parent_obj],
                    ),
                    TrailEmitter(trail_color=glm.vec3(1, 0.207, 0.207)),
                ],
            )

    def check_health(self):
        if self.parent_obj.health.value <= 0:
            self.hit_sound.set_volume(
                1
                / glm.distance(self.player.transform.position, self.parent_obj.transform.position)
                * 5
            )
            self.hit_sound.play()
            GameManager.score += 1
            self.parent_obj.destroy()

    def update_heading(self):
        leading_vector = LeadingReticle.calculate_reticle_position(
            self.parent_obj.transform.position,
            self.parent_obj.physics_body.velocity,
            self.player.transform.position,
            self.player.physics_body.velocity,
            100,
        )
        if leading_vector is None:
            leading_vector = self.player.transform.position

        self.target_rotation_quaternion = glm.quat(
            glm.inverse(
                glm.lookAt(
                    self.parent_obj.transform.position,
                    leading_vector,
                    self.parent_obj.transform.R * glm.vec3(0, 1, 0),
                )
            )
        )

        self.parent_obj.transform.quaternion = self.target_rotation_quaternion

        # -- interpolating between current and target rotation
        self.parent_obj.transform.quaternion = glm.slerp(
            self.parent_obj.transform.quaternion,
            self.target_rotation_quaternion,
            1 - Clock.delta_time * 2,
        )

        self.target_vector = self.player.transform.position - self.parent_obj.transform.position

        accel = glm.length(self.target_vector)

        self.parent_obj.physics_body.velocity += (
            self.player.transform.R * glm.vec3(0, 0, accel) * Clock.delta_time
        )

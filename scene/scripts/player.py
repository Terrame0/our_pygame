
from graphics.graphics_backend import GraphicsBackend
from scene.modules.physics_body import PhysicsBody
from scene.scripts.skybox import Skybox
from utils import custom_events
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from graphics.texture import Texture
import pygame
from pyglm import glm
from scene.scene import Camera, Scene
from scene.modules.module_base import Module
from scene.scripts.projectile import Projectile
from scene.scripts.crosshair import Crosshair
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.target_selector import TargetSelector
from utils.debug import debug


class Player(Module):
    requires = [PhysicsBody, Transform, Camera]

    def __init_module__(self):
        # -- constants
        self.collision_radius = 0.1
        self.boost_duration = 4
        self.boost_cooldown = 4
        self.max_boost_modifier = 20
        self.reload_time = 0.5

        # -- state
        self.is_boosting = False
        self.boost_modifier = 1
        self.boost_start = GraphicsBackend().clock.time_snapshot - self.boost_cooldown
        self.last_shot = GraphicsBackend().clock.time_snapshot - self.reload_time

        # -- crosshair
        self.crosshair = SceneObject(name="crosshair")
        self.crosshair.add_module(Transform)
        self.crosshair.add_module(Mesh, obj_path="assets/plane.obj")
        self.crosshair.add_module(
            Renderer,
            texture=Texture.load_from_file("assets/crosshair_3.png"),
            is_transparent=True,
            is_UI=True,
        )
        self.crosshair.add_module(TargetSelector, player=self.parent_obj)
        self.crosshair.add_module(Crosshair, player=self.parent_obj)

        # -- leading reticle
        self.reticle = SceneObject(name="reticle")
        self.reticle.add_module(Transform)
        self.reticle.add_module(Mesh, obj_path="assets/plane.obj")
        self.reticle.add_module(
            Renderer,
            texture=Texture.load_from_file("assets/reticle_2.png"),
            is_transparent=True,
            is_UI=True,
        )
        self.reticle.add_module(
            LeadingReticle,
            player=self.parent_obj,
            target_selector=self.crosshair.target_selector,
        )

        # -- skybox
        self.skybox = SceneObject(name="skybox")
        self.skybox.add_module(Transform, scale=glm.vec3(-500))
        self.skybox.add_module(Mesh, obj_path="assets/cube.obj")
        self.skybox.add_module(
            Renderer, texture=Texture.load_from_file("assets/skybox.png")
        )
        self.skybox.add_module(Skybox, player=self.parent_obj)

        # -- event subscriptions
        self.subscribe_to_event(custom_events.UPDATE, self.handle_keyboard_input)
        self.subscribe_to_event(custom_events.UPDATE, self.calculate_boost)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_mouse_input)
        self.subscribe_to_event(custom_events.UPDATE, self.shoot, pass_event=True)

    def check_collisions(self):
        for obj in Scene().objects:
            if (
                hasattr(obj, "collider")
                and obj.mesh.bounding_sphere_radius >= self.collision_radius
            ):
                distance_test: glm.vec4 = obj.collider.dist_to_point(
                    self.obj.transform.position
                )
                if (
                    obj.collider.dist_to_point(self.obj.transform.position).x
                    < self.collision_radius
                ):
                    self.obj.transform.position += (
                        distance_test.yzw
                        / glm.length(distance_test.yzw)
                        * (self.collision_radius - distance_test.x)
                    )
                    self.velocity = (
                        glm.reflect(
                            self.velocity,
                            distance_test.yzw / glm.length(distance_test.yzw),
                        )
                        * 0.3
                    )

    def shoot(self, event):
        if (
            pygame.mouse.get_pressed()[0]
            and GraphicsBackend().clock.time_snapshot - self.last_shot
            > self.reload_time
        ):
            self.last_shot = GraphicsBackend().clock.time_snapshot
            projectile = SceneObject(name="projectile")
            projectile.add_module(Transform)
            projectile.add_module(Mesh, obj_path="assets/plane.obj")
            projectile.add_module(PhysicsBody)
            projectile.physics_body.velocity = glm.vec3(1)
            projectile.add_module(
                Renderer,
                texture=Texture.load_from_file("assets/plasma.png"),
            )
            projectile.add_module(
                Projectile,
                player=self.parent_obj,
            )

    def handle_mouse_input(self):
        clock = GraphicsBackend().clock
        mpos = pygame.mouse.get_rel()

        # -- yaw
        self.parent_obj.physics_body.angular_velocity.y -= mpos[0] * clock.delta_time

        # -- pitch
        self.parent_obj.physics_body.angular_velocity.x -= mpos[1] * clock.delta_time

    def calculate_boost(self):
        x = (
            glm.clamp(
                GraphicsBackend().clock.time_snapshot - self.boost_start,
                0,
                self.boost_duration,
            )
            / self.boost_duration
        )
        if x == 0:
            self.is_boosting = True
        if x == 1:
            self.is_boosting = False
        t = (glm.cos((x * 2.43409) ** 2 + 3.5) + 1) / 2
        self.parent_obj.camera.fov = 90 + t * 15
        self.boost_modifier = 1 + t * self.max_boost_modifier

    def handle_keyboard_input(self):
        # -- translation
        d = glm.vec3(0)
        needs_update = False
        for key, vec in {
            pygame.K_w: glm.vec3(0, 0, -5),
            pygame.K_a: glm.vec3(-3, 0, 0),
            pygame.K_s: glm.vec3(0, 0, 4),
            pygame.K_d: glm.vec3(3, 0, 0),
            pygame.K_f: glm.vec3(0, -4, 0),
            pygame.K_r: glm.vec3(0, 4, 0),
        }.items():
            if pygame.key.get_pressed()[key]:
                needs_update = True
                d += vec
        clock = GraphicsBackend().clock

        # -- boost locks to full throttle forward
        if self.is_boosting:
            needs_update = True
            if d.z > 0:
                d.z = -0.2
            else:
                d.z = -2

        # -- applying velocity change
        if needs_update and d != glm.vec3(0):
            self.parent_obj.physics_body.velocity += (
                (self.parent_obj.transform.R * d)
                * clock.delta_time
                * self.boost_modifier
            )

        # -- roll
        for key, v in {
            pygame.K_q: 4,
            pygame.K_e: -4,
        }.items():
            if pygame.key.get_pressed()[key]:
                self.parent_obj.physics_body.angular_velocity.z -= v * clock.delta_time

        # -- boost
        if pygame.key.get_pressed()[pygame.K_TAB]:
            if (
                GraphicsBackend().clock.time_snapshot - self.boost_start
                > self.boost_cooldown
            ):
                self.boost_start = GraphicsBackend().clock.time_snapshot
                debug.log("boosting!")
                self.is_boosting = True

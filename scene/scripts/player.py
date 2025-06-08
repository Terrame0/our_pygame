
from graphics.graphics_backend import GraphicsBackend
from scene.modules.physics_body import PhysicsBody
from scene.scripts import crosshair
from scene.scripts.skybox import Skybox
from utils import custom_events
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.camera import Camera
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from graphics.texture import Texture
import pygame
from pyglm import glm
from utils.debug import debug
from scene.scene import Scene
from scene.modules.module_base import Module

from scene.scripts.projectile import Projectile
from scene.scripts.crosshair import Crosshair
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.target_selector import TargetSelector


class Player(Module):
    requires = [PhysicsBody, Transform]

    def __init_module__(self):
        # -- constants
        self.collision_radius = 0.1

        # -- crosshair
        self.crosshair = SceneObject(name="crosshair")
        self.crosshair.add_module(Transform)
        self.crosshair.add_module(Mesh, obj_path="assets/plane.obj")
        self.crosshair.add_module(
            Renderer,
            texture=Texture(0, "assets/crosshair_3.png"),
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
            texture=Texture(0, "assets/reticle_2.png"),
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
        self.skybox.add_module(Renderer, texture=Texture(0, "assets/skybox.png"))
        self.skybox.add_module(Skybox, player=self.parent_obj)

        # -- event subscriptions
        self.subscribe_to_event(custom_events.UPDATE, self.handle_keyboard_input)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_mouse_input)
        self.subscribe_to_event(pygame.MOUSEBUTTONDOWN, self.shoot, pass_event=True)

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
        if event.button == 1:
            projectile = SceneObject(name="projectile")
            projectile.add_module(Transform)
            projectile.add_module(Mesh, obj_path="assets/plane.obj")
            projectile.add_module(PhysicsBody)
            projectile.physics_body.velocity = glm.vec3(1)
            projectile.add_module(
                Renderer,
                texture=Texture(0, "assets/plasma.png"),
            )
            projectile.add_module(
                Projectile,
                player=self.parent_obj,
            )

    def handle_mouse_input(self):
        mpos = pygame.mouse.get_rel()

        # -- yaw
        self.parent_obj.physics_body.angular_velocity.y -= mpos[0] / 100

        # -- pitch
        self.parent_obj.physics_body.angular_velocity.x -= mpos[1] / 100

    def handle_keyboard_input(self):
        # -- translation
        d = glm.vec3(0)
        needs_update = False
        for key, vec in {
            pygame.K_w: glm.vec3(0, 0, -1),
            pygame.K_a: glm.vec3(-1, 0, 0),
            pygame.K_s: glm.vec3(0, 0, 1),
            pygame.K_d: glm.vec3(1, 0, 0),
            pygame.K_LCTRL: glm.vec3(0, -1, 0),
            pygame.K_SPACE: glm.vec3(0, 1, 0),
        }.items():
            if pygame.key.get_pressed()[key]:
                needs_update = True
                d += vec
        clock = GraphicsBackend().clock
        if needs_update and d != glm.vec3(0):
            self.parent_obj.physics_body.velocity += (
                self.parent_obj.transform.R * d
            ) / 50

        # -- roll
        for key, v in {
            pygame.K_q: 1,
            pygame.K_e: -1,
        }.items():
            if pygame.key.get_pressed()[key]:
                self.parent_obj.physics_body.angular_velocity.z -= v / 50

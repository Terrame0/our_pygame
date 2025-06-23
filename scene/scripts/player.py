from graphics.graphics_backend import GraphicsBackend
from scene.modules.physics_body import PhysicsBody
from scene.scripts.skybox import Skybox
from scene.scripts.speed_lines_emitter import SpeedLinesEmitter
from scene.scripts.trail_emitter import TrailEmitter
from utils import custom_events
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from graphics.texture import Texture
import pygame
from pyglm import glm
from scene.scene import Scene
from scene.modules.camera import Camera
from scene.modules.module_base import Module
from scene.scripts.projectile import Projectile
from scene.scripts.crosshair import Crosshair
from scene.scripts.health import Health
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.target_selector import TargetSelector
from scene.scripts.weapons.weapon_controller import WeaponController
from utils.debug import debug
from utils.path_resolver import resolve_path


class Player(Module):
    requires = [PhysicsBody, Transform, Camera, Health]

    def __init_module__(self):
        self.shoot_sound = pygame.mixer.Sound(resolve_path("assets/sounds/shoot.mp3"))
        self.hit_sound = pygame.mixer.Sound(resolve_path("assets/sounds/hit.mp3"))
        self.boost_sound = pygame.mixer.Sound(resolve_path("assets/sounds/boost.mp3"))

        # -- constants
        self.collision_radius = 0.1
        self.boost_duration = 4
        self.boost_cooldown = 4
        self.max_boost_modifier = 20

        # -- state
        self.stop = False
        self.is_boosting = False
        self.boost_modifier = 1
        self.boost_start = GraphicsBackend().clock.now - self.boost_cooldown

        # -- crosshair
        self.crosshair = SceneObject(
            name="crosshair",
            modules=[
                Transform,
                Mesh(path="assets/meshes/plane.obj"),
                Renderer(
                    texture=Texture.load_from_file("assets/textures/crosshair.png"),
                    is_transparent=True,
                    is_UI=True,
                ),
                Crosshair(player=self.parent_obj),
            ],
        )

        # -- leading reticle
        self.reticle = SceneObject(
            name="reticle",
            modules=[
                Transform(),
                Mesh(path="assets/meshes/plane.obj"),
                Renderer(
                    texture=Texture.load_from_file("assets/textures/reticle.png"),
                    is_transparent=True,
                    is_UI=True,
                ),
                TargetSelector(player=self.parent_obj),
                LeadingReticle(
                    player=self.parent_obj,
                ),
                WeaponController(
                    owner=self.parent_obj,
                ),
            ],
        )

        # -- skybox
        self.skybox = SceneObject(
            name="skybox",
            modules=[
                Transform(scale=glm.vec3(-500)),
                Mesh(path="assets/meshes/cube.obj"),
                Renderer(texture=Texture.load_from_file("assets/textures/skybox.png")),
                Skybox(player=self.parent_obj),
            ],
        )

        # -- speed lines
        self.speed_lines = SceneObject(
            name="skybox", modules=[SpeedLinesEmitter(player=self.parent_obj)]
        )

        # -- event subscriptions
        self.subscribe_to_event(custom_events.UPDATE, self.handle_keyboard_input)
        self.subscribe_to_event(custom_events.UPDATE, self.calculate_boost)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_mouse_input)
        self.subscribe_to_event(custom_events.UPDATE, self.shoot)
        self.subscribe_to_event(custom_events.UPDATE, self.check_health)

    def check_health(self):
        if self.parent_obj.health.value <= 0:
            self.hit_sound.play()
            self.stop = True

    def shoot(self):
        if pygame.mouse.get_pressed()[0]:
            self.reticle.weapon_controller.shoot_weapons()

    def handle_mouse_input(self):
        clock = GraphicsBackend().clock
        mpos = pygame.mouse.get_rel()

        # -- yaw
        self.parent_obj.physics_body.angular_velocity.y -= mpos[0] / 100

        # -- pitch
        self.parent_obj.physics_body.angular_velocity.x -= mpos[1] / 100

    def calculate_boost(self):
        x = (
            glm.clamp(
                GraphicsBackend().clock.now - self.boost_start,
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
            if GraphicsBackend().clock.now - self.boost_start > self.boost_cooldown:
                self.boost_sound.play()
                self.boost_start = GraphicsBackend().clock.now
                debug.log("boosting!")
                self.is_boosting = True

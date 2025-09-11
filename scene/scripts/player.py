from pyglm import glm


from core.event_system.user_events import UserEvents
from utils.path_resolver import resolve_path
from graphics.resources.texture import Texture

from core.clock import Clock

from scene.scene_object import SceneObject
from scene.modules.module_base import Module

from scene.modules.physics_body import PhysicsBody
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.camera import Camera

from scene.scripts.skybox import Skybox
from scene.scripts.speed_lines_emitter import SpeedLinesEmitter
from scene.scripts.crosshair import Crosshair
from scene.scripts.health import Health
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.target_selector import TargetSelector
from scene.scripts.weapons.weapon_controller import WeaponController


class Player(Module):
    requires = [PhysicsBody, Transform, Camera, Health]

    def __init_module__(self):

        # -- constants
        self.collision_radius = 0.1
        self.boost_duration = 4
        self.boost_cooldown = 4
        self.max_boost_modifier = 20

        # -- state
        self.stop = False
        self.is_boosting = False
        self.boost_modifier = 1
        self.boost_start = Clock.now - self.boost_cooldown

        # -- crosshair
        # self.crosshair = SceneObject(
        #    name="crosshair",
        #    modules=[
        #        Transform,
        #        Renderer(
        #            mesh="plane.obj",
        #            texture="crosshair.png",
        #            is_transparent=True,
        #            is_UI=True,
        #        ),
        #        Crosshair(player=self.parent_obj),
        #    ],
        # )

        # -- leading reticle
        # self.reticle = SceneObject(
        #    name="reticle",
        #    modules=[
        #        Transform,
        #        Renderer(
        #            mesh="plane.obj",
        #            texture="reticle.png",
        #            is_transparent=True,
        #            is_UI=True,
        #        ),
        #        TargetSelector(player=self.parent_obj),
        #        LeadingReticle(player=self.parent_obj),
        #        WeaponController(owner=self.parent_obj),
        #    ],
        # )

        # -- move this to scene

        # -- skybox
        # self.skybox = SceneObject(
        #    name="skybox",
        #    modules=[
        #        Transform(scale=glm.vec3(-500)),
        #        Mesh(path="assets/meshes/cube.obj"),
        #        Renderer(texture=Texture.load_from_file("assets/textures/skybox.png")),
        #        Skybox(player=self.parent_obj),
        #    ],
        # )

        # -- speed lines
        self.speed_lines = SceneObject(
            name="speed_lines", modules=[SpeedLinesEmitter(player=self.parent_obj)]
        )

        # -- event subscriptions
        self.subscribe_to_event(UserEvents.get_id("update"), self.handle_keyboard_input)
        self.subscribe_to_event(UserEvents.get_id("update"), self.calculate_boost)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_mouse_input)
        self.subscribe_to_event(UserEvents.get_id("update"), self.shoot)
        self.subscribe_to_event(UserEvents.get_id("update"), self.check_health)

    def check_health(self):
        if self.parent_obj.health.value <= 0:
            self.stop = True

    def shoot(self):
        if pygame.mouse.get_pressed()[0]:
            self.reticle.weapon_controller.shoot_weapons()

    def handle_mouse_input(self):
        mpos = pygame.mouse.get_rel()

        # -- yaw
        self.parent_obj.physics_body.angular_velocity.y -= mpos[0] / 100

        # -- pitch
        self.parent_obj.physics_body.angular_velocity.x -= mpos[1] / 100

    def calculate_boost(self):
        x = (
            glm.clamp(
                Clock.now - self.boost_start,
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
                (self.parent_obj.transform.R * d) * Clock.delta_time * self.boost_modifier
            )

        # -- roll
        for key, v in {
            pygame.K_q: 4,
            pygame.K_e: -4,
        }.items():
            if pygame.key.get_pressed()[key]:
                self.parent_obj.physics_body.angular_velocity.z -= v * Clock.delta_time

        # -- boost
        if pygame.key.get_pressed()[pygame.K_TAB]:
            if Clock.now - self.boost_start > self.boost_cooldown:
                self.boost_start = Clock.now
                self.is_boosting = True

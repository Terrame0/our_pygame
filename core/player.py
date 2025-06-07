
from graphics.graphics_backend import GraphicsBackend
from utils import custom_events
from core.event_manager import EventManager
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.camera import Camera
from core.projectile import Projectile
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from graphics.texture import Texture
import pygame
from pyglm import glm
from utils.debug import debug
from scene.scene import Scene
from core.leading_reticle import LeadingReticle
from scene.scripts.script_base import Script


# -- turn this into a script module descender
class Player:
    def __init__(self):
        # -- constants
        self.collision_radius = 0.1

        # -- state
        self.angular_velocity = glm.vec3(0)
        self.velocity = glm.vec3(0)

        # -- containers
        self.projectile_list = []

        # -- leading reticle
        self.reticle = LeadingReticle(self)

        # -- player scene object
        self.obj = SceneObject(name="player")
        self.obj.add_module(Transform, position=glm.vec3(0, 0, 5))
        self.obj.add_module(Camera)

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

        # -- target
        self.target = SceneObject(name="target")
        self.target.add_module(Transform)
        self.target.add_module(Mesh, obj_path="assets/plane.obj")
        self.target.add_module(
            Renderer,
            texture=Texture(0, "assets/target.png"),
            is_transparent=True,
            is_UI=True,
        )

        # -- skybox
        self.skybox = SceneObject(name="skybox")
        self.skybox.add_module(Transform, scale=glm.vec3(500))
        self.skybox.add_module(Mesh, obj_path="assets/cube.obj")
        self.skybox.add_module(Renderer, texture=Texture(0, "assets/skybox.png"))

        # -- event manager subscriptions
        EventManager().subscribe(
            pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False
        )
        EventManager().subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

        EventManager().subscribe(custom_events.UPDATE, self.handle_keyboard_input)
        EventManager().subscribe(custom_events.UPDATE, self.run_physics)
        EventManager().subscribe(custom_events.UPDATE, self.move_skybox)
        EventManager().subscribe(custom_events.UPDATE, self.check_collisions)
        EventManager().subscribe(custom_events.UPDATE, self.move_crosshair)

        EventManager().subscribe(pygame.MOUSEMOTION, self.handle_mouse_input)
        EventManager().subscribe(pygame.MOUSEBUTTONDOWN, self.shoot, pass_event=True)

    def check_collisions(self):
        for obj in Scene().object_list:
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
            self.projectile_list.append(Projectile(self))

    def move_skybox(self):
        self.skybox.transform.position = self.obj.transform.position

    def move_crosshair(self):
        self.crosshair.transform.position = (
            self.obj.transform.position + self.obj.transform.R * glm.vec3(0, 0, -1)
        )

    def handle_mouse_input(self):
        clock = GraphicsBackend().clock
        mpos = pygame.mouse.get_rel()

        self.angular_velocity.y -= mpos[0] / 100
        self.angular_velocity.x -= mpos[1] / 100

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
            self.velocity += (self.obj.transform.R * d) / 50

        # -- roll
        for key, v in {
            pygame.K_q: 1,
            pygame.K_e: -1,
        }.items():
            if pygame.key.get_pressed()[key]:
                self.angular_velocity.z -= v / 50

    def run_physics(self):
        clock = GraphicsBackend().clock

        # -- velocity calculation
        delta_velocity = self.velocity * clock.delta_time
        self.obj.transform.position += delta_velocity

        # -- rotation axis calculation (can be done less often)
        yaw_axis = self.obj.transform.R * glm.vec3(0, 1, 0)
        pitch_axis = self.obj.transform.R * glm.vec3(1, 0, 0)
        roll_axis = self.obj.transform.R * glm.vec3(0, 0, -1)

        # -- rotation calculation
        delta_angular_velocity = self.angular_velocity * clock.delta_time
        pitch = glm.quat(
            glm.cos(delta_angular_velocity.x / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.x / 2)) * pitch_axis)
        )
        yaw = glm.quat(
            glm.cos(delta_angular_velocity.y / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.y / 2)) * yaw_axis)
        )
        roll = glm.quat(
            glm.cos(delta_angular_velocity.z / 2),
            *(glm.vec3(glm.sin(delta_angular_velocity.z / 2)) * roll_axis)
        )
        self.obj.transform.quaternion = (
            pitch * yaw * roll * self.obj.transform.quaternion
        )

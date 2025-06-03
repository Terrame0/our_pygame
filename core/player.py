
from graphics.graphics_backend import GraphicsBackend
from utils import custom_events
from core.event_manager import EventManager
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.camera import Camera
import pygame
from pyglm import glm


class Player:
    def __init__(self):
        self.angular_velocity = glm.vec3(0)
        self.velocity = glm.vec3(0)
        self.obj = SceneObject(name="player")
        self.obj.add_module(Transform)
        self.obj.add_module(Camera)

        EventManager().subscribe(
            pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False
        )
        EventManager().subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)

        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

        EventManager().subscribe(custom_events.UPDATE, self.wasd_move)
        EventManager().subscribe(pygame.MOUSEMOTION, self.look_around)
        EventManager().subscribe(custom_events.UPDATE, self.run_physics)

    def run_physics(self):
        clock = GraphicsBackend().clock
        for key, a in {
            pygame.K_q: -1,
            pygame.K_e: 1,
        }.items():
            if pygame.key.get_pressed()[key]:
                self.angular_velocity.z -= a * clock.delta_time / 100

        self.obj.transform.position += self.velocity

        yaw_axis = self.obj.transform.R * glm.vec3(0, 1, 0)
        pitch_axis = self.obj.transform.R * glm.vec3(1, 0, 0)
        roll_axis = self.obj.transform.R * glm.vec3(0, 0, 1)

        pitch = glm.quat(
            glm.cos(self.angular_velocity.x / 2),
            *(glm.vec3(glm.sin(self.angular_velocity.x / 2)) * pitch_axis)
        )
        yaw = glm.quat(
            glm.cos(self.angular_velocity.y / 2),
            *(glm.vec3(glm.sin(self.angular_velocity.y / 2)) * yaw_axis)
        )
        roll = glm.quat(
            glm.cos(self.angular_velocity.z / 2),
            *(glm.vec3(glm.sin(self.angular_velocity.z / 2)) * roll_axis)
        )



        self.obj.transform.quaternion = pitch * yaw * roll * self.obj.transform.quaternion

    def wasd_move(self):
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
            self.velocity += (self.obj.transform.R * d) * clock.delta_time / 1000

    def look_around(self):
        clock = GraphicsBackend().clock
        mpos = pygame.mouse.get_rel()
        

        self.angular_velocity.y -= mpos[0] * clock.delta_time / 100
        self.angular_velocity.x -= mpos[1] * clock.delta_time / 100




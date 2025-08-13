from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.camera import Camera
from core.clock import Clock
import pygame


class CameraController(Module):
    requires = [Transform, Camera]

    def __init_module__(self):

        self.needs_update = True
        self.parent_obj.transform.position = glm.vec3(0, 0, 10)

        self.phi = 0
        self.theta = 0
        self.rotation_angle = glm.vec2(0)

        self.zoom_power = 3.0
        self.zoom_base = 2.0

        self.pivot_point = glm.vec3(0)
        self.offset_direction = glm.vec3(0, 0, 1)

        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_panning, pass_event=True)
        self.subscribe_to_event(pygame.MOUSEMOTION, self.handle_rotation, pass_event=True)
        self.subscribe_to_event(pygame.MOUSEWHEEL, self.handle_zoom, pass_event=True)
        self.subscribe_to_event(custom_events.UPDATE, self.update_transform)

    @property
    def offset_vector(self):
        return self.direction_vector * self.zoom_modifier

    @property
    def rotation_angle(self):
        return None

    @rotation_angle.setter
    def rotation_angle(self, value):
        self.phi = self.phi + value.x
        self.theta = glm.clamp(self.theta + value.y, -glm.pi() / 2 + 0.01, glm.pi() / 2 - 0.01)

        self.direction_vector = glm.vec3(
            glm.sin(self.phi) * glm.cos(self.theta),
            glm.sin(self.theta),
            glm.cos(self.phi) * glm.cos(self.theta),
        )

    @property
    def zoom_modifier(self):
        return self.zoom_base**self.zoom_power

    def handle_rotation(self, event):
        if pygame.mouse.get_pressed()[1] and not pygame.key.get_pressed()[pygame.K_LSHIFT]:
            motion = glm.vec2(-event.rel[0], event.rel[1]) / 300
            self.rotation_angle = motion
            self.needs_update = True

    def handle_panning(self, event):
        if pygame.mouse.get_pressed()[1] and pygame.key.get_pressed()[pygame.K_LSHIFT]:
            motion = glm.vec2(-event.rel[0], event.rel[1]) / 500 * self.zoom_modifier
            right = self.parent_obj.transform.R * glm.vec3(1, 0, 0)
            up = self.parent_obj.transform.R * glm.vec3(0, 1, 0)

            self.pivot_point += motion.x * right + motion.y * up
            self.needs_update = True

    def handle_zoom(self, event):
        self.zoom_power = glm.clamp(self.zoom_power - event.y / 5, -10, 10)
        self.needs_update = True

    def update_transform(self):
        if self.needs_update:
            self.parent_obj.transform.position = self.pivot_point + self.offset_vector
            self.parent_obj.transform.quaternion = glm.quat(
                glm.inverse(
                    glm.lookAt(
                        self.pivot_point + self.offset_vector,
                        self.pivot_point,
                        glm.vec3(0, 1, 0),
                    )
                )
            )
            self.needs_update = False

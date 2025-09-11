from sdl2 import SDL_MOUSEMOTION, SDL_SCANCODE_LSHIFT, SDL_MOUSEWHEEL
from core.event_system.user_events import UserEvents
from scene.modules.transform import Transform
from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.camera import Camera
from graphics.window import Window
from core.event_system.user_events import UserEvents
from utils.user_input import UserInput


class CameraController(Module):
    requires = [Transform, Camera]

    def __init_module__(self):

        self.needs_update = True

        self.phi = 0
        self.theta = 0
        self.rotation_angle = glm.vec2(0)

        self.zoom_power = 3.0
        self.zoom_base = 2.0

        self.pivot_point = glm.vec3(0)
        self.offset_direction = glm.normalize(glm.vec3(1))

        self.subscribe_to_event(SDL_MOUSEMOTION, self.handle_panning, pass_event=True)
        self.subscribe_to_event(SDL_MOUSEMOTION, self.handle_rotation, pass_event=True)
        self.subscribe_to_event(SDL_MOUSEWHEEL, self.handle_zoom, pass_event=True)
        self.subscribe_to_event(UserEvents.get_id("update"), self.update_transform)

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
        if (UserInput.mbutton(1) or UserInput.mbutton(2)) and not UserInput.key(
            SDL_SCANCODE_LSHIFT
        ):
            motion = glm.vec2(-event.motion.xrel, event.motion.yrel) / 300
            self.rotation_angle = motion
            self.needs_update = True

    def handle_panning(self, event):
        if (UserInput.mbutton(1) or UserInput.mbutton(2)) and UserInput.key(SDL_SCANCODE_LSHIFT):
            motion = (
                glm.vec2(-event.motion.xrel, event.motion.yrel)
                / glm.vec2(*Window.size)
                * self.zoom_modifier
                * 2
            )
            right = self.parent_obj.transform.R * glm.vec3(1, 0, 0)
            up = self.parent_obj.transform.R * glm.vec3(0, 1, 0)

            self.pivot_point += motion.x * right + motion.y * up
            self.needs_update = True

    def handle_zoom(self, event):
        self.zoom_power = glm.clamp(self.zoom_power - event.wheel.y / 5, -10, 10)
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

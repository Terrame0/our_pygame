
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


# -- turn this into a script module descender
class LeadingReticle:
    def __init__(self, parent):
        self.parent = parent
        EventManager().subscribe(custom_events.UPDATE, self.update)

        self.obj = SceneObject(name="reticle")
        self.obj.add_module(Transform, scale=glm.vec3(0.01))
        self.obj.add_module(Mesh, obj_path="assets/plane.obj")
        self.obj.add_module(
            Renderer,
            texture=Texture(0, "assets/reticle_2.png"),
            is_transparent=True,
            is_UI=True,
        )

    def update(self):
        self.obj.transform.position = self.calculate_reticle_position(
            self.parent.obj.transform.position,
            self.parent.velocity,
            glm.vec3(0),
            glm.vec3(0),
            10,
        )


    # MAY NOT WORK CORRECTLY FOR MOVING TARGETS (YET)
    def calculate_reticle_position(
        self,
        player_position: glm.vec3,
        player_velocity: glm.vec3,
        target_position: glm.vec3,
        target_velocity: glm.vec3,
        projectile_speed: float,
    ) -> glm.vec3:
        if projectile_speed <= 0:
            return target_position

        relative_velocity = target_velocity - player_velocity
        position_delta = target_position - player_position

        if glm.length(relative_velocity) < 1e-5:
            return target_position

        a = glm.length2(relative_velocity) - projectile_speed**2
        b = 2.0 * glm.dot(relative_velocity, position_delta)
        c = glm.length2(position_delta)

        if abs(a) < 1e-5:
            if abs(b) < 1e-5:  # No solution
                return target_position
            t = -c / b
            return target_position + target_velocity * max(t, 0)

        # 6. Solve quadratic
        discriminant = b**2 - 4 * a * c

        # Case 1: No real solution
        if discriminant < 0:
            return target_position

        sqrt_discriminant = glm.sqrt(discriminant)
        t1 = (-b + sqrt_discriminant) / (2 * a)
        t2 = (-b - sqrt_discriminant) / (2 * a)

        # 7. Filter valid times
        valid_times = [t for t in (t1, t2) if t > 0]

        if valid_times:
            t = min(valid_times)  # Earliest interception
        else:
            # Use least negative time for visual continuity
            t = min(t1, t2, key=abs)

        return target_position + relative_velocity * max(t, 0)

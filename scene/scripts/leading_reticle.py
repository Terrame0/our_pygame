from scene.scripts.target_selector import TargetSelector
from utils import custom_events
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from pyglm import glm
from scene.modules.module_base import Module


class LeadingReticle(Module):
    requires = [Transform, Mesh, Renderer]

    def __init_module__(self, player: SceneObject, target_selector: TargetSelector):
        self.target_selector = target_selector
        self.player = player
        self.subscribe_to_event(custom_events.UPDATE, self.update)

    def update(self):
        self.parent_obj.renderer.is_visible = False
        if self.target_selector.selected_target is not None:
            pos = self.calculate_reticle_position(
                self.player.transform.position,
                self.player.physics_body.velocity,
                self.target_selector.selected_target.transform.position,
                self.target_selector.selected_target.physics_body.velocity,
                10,
            )
            if pos is not None:
                self.parent_obj.renderer.is_visible = True
                self.parent_obj.transform.position = pos

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
            if abs(b) < 1e-5:  # -- no solution
                return None
            t = -c / b
            return target_position + target_velocity * max(t, 0)

        discriminant = b**2 - 4 * a * c

        # -- no solution
        if discriminant < 0:
            return None

        sqrt_discriminant = glm.sqrt(discriminant)
        t1 = (-b + sqrt_discriminant) / (2 * a)
        t2 = (-b - sqrt_discriminant) / (2 * a)

        valid_times = [t for t in (t1, t2) if t > 0]

        if valid_times:
            t = min(valid_times)  # -- earliest interception
        else:
            # -- use least negative time for visual continuity
            t = min(t1, t2, key=abs)

        return target_position + relative_velocity * max(t, 0)

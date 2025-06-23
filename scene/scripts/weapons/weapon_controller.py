from typing import List
from scene.modules.collider import PhysicsBody
from utils import custom_events
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from scene.scripts.weapons.cannon import Cannon
from scene.scripts.leading_reticle import LeadingReticle
from scene.scripts.target_selector import TargetSelector
from scene.scene_object import SceneObject
from graphics.texture import Texture
from pyglm import glm
from scene.modules.module_base import Module
from core.clock import Clock
from utils.debug import debug


class WeaponController(Module):
    requires = [Transform, LeadingReticle, TargetSelector]

    def __init_module__(self, owner: SceneObject):
        self.owner = owner
        self.leading_reticle = self.parent_obj.leading_reticle
        self.weapons: List = []

        cannon = SceneObject(
            name="cannon",
            modules=[
                Transform(),
                PhysicsBody(),
                Mesh(path="assets/meshes/gun.obj"),
                Renderer(texture=Texture.load_from_file("assets/textures/gun.png")),
                Cannon(),
            ],
        )

        self.weapons.append(cannon)

        self.subscribe_to_event(custom_events.UPDATE, self.update)

    def shoot_weapons(self):
        for weapon in self.weapons:
            weapon.cannon.shoot(self.owner)

    # -- TODO move most of this code into the cannon class
    def update(self):
        for weapon in self.weapons:
            weapon.transform.position = (
                self.owner.transform.position
                + self.owner.transform.R * glm.vec3(1, -0.5, -1.5)
            )

            if (
                self.parent_obj.target_selector.selected_target is not None
                and glm.dot(
                    glm.normalize(  # -- target vector
                        self.parent_obj.target_selector.selected_target.transform.position
                        - self.owner.transform.position
                    ),
                    self.owner.transform.R * glm.vec3(0, 0, -1),  # -- view vector
                )
                > 0.95
            ):
                leading_vector = LeadingReticle.calculate_reticle_position(
                    weapon.transform.position,
                    self.owner.physics_body.velocity,
                    self.parent_obj.target_selector.selected_target.transform.position,
                    self.parent_obj.target_selector.selected_target.physics_body.velocity,
                    100,
                )

                target_rotation_quaternion = glm.quat(
                    glm.inverse(
                        glm.lookAt(
                            weapon.transform.position,
                            leading_vector,
                            self.owner.transform.R * glm.vec3(0, 1, 0),
                        )
                    )
                )
            else:
                target_rotation_quaternion = self.owner.transform.quaternion

            weapon.transform.quaternion = glm.slerp(
                weapon.transform.quaternion,
                target_rotation_quaternion,
                Clock().delta_time * 10,
            )

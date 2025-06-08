import pygame
from utils import custom_events
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.mesh import Mesh
from scene.modules.renderer import Renderer
from graphics.texture import Texture
from pyglm import glm
from scene.modules.module_base import Module
from scene.scene import Scene
from scene.scripts.target_indicator import TargetIndicator


class TargetSelector(Module):
    def __init_module__(self, player: SceneObject):
        self.player = player
        self.selected_target = None
        self.subscribe_to_event(custom_events.UPDATE, self.update)
        self.subscribe_to_event(pygame.KEYDOWN, self.select_target, pass_event=True)
        self.available_targets = {}

    def update(self):
        for target in Scene().objects:
            if (
                hasattr(target, "enemy")
                and not target.renderer.is_UI
                and target not in self.available_targets
            ):
                self.available_targets[target] = self.create_indicator(target)

        for target in list(self.available_targets.keys()):
            if target not in Scene().objects:
                self.available_targets.pop(target).destroy()

    def create_indicator(self, target: SceneObject) -> SceneObject:
        indicator = SceneObject(name="indicator")
        indicator.add_module(Transform)
        indicator.add_module(Mesh, obj_path="assets/plane.obj")
        indicator.add_module(Renderer, is_transparent=True, is_UI=True)
        indicator.renderer.texture = Texture(0, "assets/target.png")
        indicator.add_module(TargetIndicator, self.player, target)
        return indicator

    def select_target(self, event):
        if event.key == pygame.K_t and self.available_targets:
            self.selected_target = max(
                self.available_targets.keys(),
                key=lambda obj: glm.dot(
                    glm.normalize(
                        obj.transform.position - self.player.transform.position
                    ),
                    self.player.transform.R * glm.vec3(0, 0, -1),
                ),
            )
            print(f"selected {self.selected_target}")

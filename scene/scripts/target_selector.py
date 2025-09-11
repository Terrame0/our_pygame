
from core.event_system.user_events import UserEvents
from scene.modules.transform import Transform
from scene.scene_object import SceneObject
from scene.modules.renderer import Renderer
from graphics.resources.texture import Texture
from pyglm import glm
from scene.modules.module_base import Module
from scene.scene import Scene
from scene.scripts.target_indicator import TargetIndicator
from utils.debug import debug


class TargetSelector(Module):
    def __init_module__(self, player: SceneObject):
        self.player = player
        self.selected_target = None
        self.subscribe_to_event(UserEvents.get_id("update"), self.update)
        self.subscribe_to_event(pygame.KEYDOWN, self.select_target, pass_event=True)
        self.available_targets = {}

    def update(self):
        for target in Scene.objects:
            if (
                hasattr(target, "enemy")
                and not target.renderer.is_UI
                and target not in self.available_targets
            ):
                self.available_targets[target] = self.create_indicator(target)

        for target in list(self.available_targets.keys()):
            if target not in Scene.objects:
                self.available_targets.pop(target).destroy()
                if target is self.selected_target:
                    self.selected_target = None

    def create_indicator(self, target: SceneObject) -> SceneObject:
        indicator = SceneObject(
            name="indicator",
            modules=[
                Transform(),
                Renderer(
                    mesh="plane.obj",
                    texture="target_inactive.png",
                    is_transparent=True,
                    is_UI=True,
                ),
                TargetIndicator(self.player, target),
            ],
        )
        return indicator

    def select_target(self, event):
        if event.key == pygame.K_t and self.available_targets:
            if self.selected_target is not None:
                self.available_targets[self.selected_target].renderer.texture = (
                    self.inactive_texture
                )
            self.selected_target = max(
                self.available_targets.keys(),
                key=lambda obj: glm.dot(
                    glm.normalize(obj.transform.position - self.player.transform.position),
                    self.player.transform.R * glm.vec3(0, 0, -1),
                ),
            )
            self.available_targets[self.selected_target].renderer.texture = "target.png"

            debug.log(f"selected {self.selected_target}")

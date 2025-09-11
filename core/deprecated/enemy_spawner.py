from scene.modules.physics_body import PhysicsBody
from scene.scripts.enemy import Enemy
from utils.singleton_decorator import singleton
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.collider import Collider
from scene.scene_object import SceneObject
from pyglm import glm
from scene.scripts.health import Health
from OpenGL.GL import *
import random
from core.clock import Clock
from core.game_manager import GameManager
from core.asset_loader import AssetLoader


@singleton
class EventManager:
    def __init__(self):
        self.player = GameManager.player
        self.group_size = 3
        self.max_group_size = 10
        self.spawn_delay = 3
        self.spawn_request_time = Clock.start_time
        self.spawn_pending = True

    def spawn_enemies(self, group_size: int, group_position: glm.vec3):
        for i in range(group_size):
            position = (
                glm.normalize(glm.vec3(*[random.random() - 0.5 for x in range(3)])) * 20
            ) + group_position

            rotation = glm.vec3(*[random.random() - 0.5 for x in range(3)]) * 360

            GameManager.enemies_alive += 1
            enemy = SceneObject(
                name=f"enemy_{i}",
                modules=[
                    Transform(position=position, rotation=rotation),
                    Mesh(path="assets/meshes/monocarrier.obj"),
                    Renderer(texture=AssetLoader().get_texture("monocarrier.png")),
                    PhysicsBody(collision_radius=1.5),
                    Collider(),
                    Health(1),
                    Enemy(player=self.player),
                ],
            )

    def update(self):
        if GameManager.enemies_alive == 0:  # -- the scene is empty, then:
            if not self.spawn_pending:  # -- if not waiting for spawn delay
                self.spawn_request_time = Clock.now
                self.spawn_pending = True  # -- queue spawn
            elif (  # -- else wait for said delay
                Clock.now - self.spawn_request_time >= self.spawn_delay
            ):
                self.spawn_pending = False
                self.spawn_enemies(
                    self.group_size,
                    glm.normalize(glm.vec3(*[random.random() - 0.5 for x in range(3)])) * 10,
                )
                if self.group_size < self.max_group_size:
                    self.group_size += 1

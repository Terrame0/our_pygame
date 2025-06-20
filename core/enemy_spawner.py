from core.event_manager import EventManager
from scene.modules.physics_body import PhysicsBody
from scene.scripts.enemy import Enemy
from utils.singleton_decorator import singleton
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.collider import Collider
from scene.scene_object import SceneObject
from scene.scene import Scene
from pyglm import glm
from scene.scripts.player import Player
from scene.modules.camera import Camera
from scene.scripts.health import Health
from graphics.texture import Texture
from OpenGL.GL import *
import random
from core.clock import Clock
from utils.debug import debug
from core.game_manager import GameManager


@singleton
class EnemySpawner:
    def __init__(self):
        self.player = GameManager().player
        self.group_size = 2
        self.spawn_delay = 3
        self.spawn_request_time = Clock().start_time
        self.spawn_pending = True

    def spawn_enemies(self, group_size: int, group_position: glm.vec3):
        for i in range(group_size):
            position = (
                glm.normalize(glm.vec3(*[random.random() - 0.5 for x in range(3)])) * 20
            ) + group_position

            rotation = glm.vec3(*[random.random() - 0.5 for x in range(3)]) * 360

            GameManager().enemies_alive += 1
            enemy = SceneObject(name=f"enemy")
            enemy.add_module(Transform, position=position, rotation=rotation)
            enemy.add_module(Mesh, path=f"assets/meshes/monocarrier.obj")
            enemy.add_module(Renderer)
            enemy.add_module(PhysicsBody, collision_radius=1)
            enemy.add_module(Collider)
            enemy.add_module(Health, 1)
            enemy.add_module(Enemy, player=self.player)
            enemy.renderer.texture = Texture.load_from_file(
                path="assets/textures/monocarrier.png"
            )

    def update(self):
        if GameManager().enemies_alive == 0:  # -- the scene is empty, then:
            if not self.spawn_pending:  # -- if not waiting for spawn delay
                self.spawn_request_time = Clock().now
                self.spawn_pending = True  # -- queue spawn
            elif (  # -- else wait for said delay
                Clock().now - self.spawn_request_time >= self.spawn_delay
            ):
                self.spawn_pending = False
                self.spawn_enemies(
                    self.group_size,
                    glm.normalize(glm.vec3(*[random.random() - 0.5 for x in range(3)]))
                    * 100,
                )
                if self.group_size < 5:
                    self.group_size += 1

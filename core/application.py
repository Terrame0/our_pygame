from graphics.graphics_backend import GraphicsBackend
from core.event_manager import EventManager
from scene.modules.physics_body import PhysicsBody
from utils.singleton_decorator import singleton
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.collider import Collider
from scene.scene_object import SceneObject
from scene.scene import Scene
from pyglm import glm
from graphics.texture import Texture
from OpenGL.GL import *
import random
from core.game_manager import GameManager
from core.enemy_spawner import EnemySpawner
import pygame
import sys


@singleton
class Application:
    def __init__(self):
        EventManager()
        GraphicsBackend()
        GameManager()

    def run(self):
        self.is_running = True
        for i in range(20):
            asteroid_type = glm.clamp(round(random.random() * 5), 1, 5)
            position = glm.vec3(*[random.random() - 0.5 for x in range(3)]) * 100
            scale = glm.vec3(random.random()) * 5 + 1
            rotation = glm.vec3(*[random.random() - 0.5 for x in range(3)]) * 360

            asteroid = SceneObject(name=f"asteroid_{asteroid_type}")
            asteroid.add_module(
                Transform, position=position, rotation=rotation, scale=scale
            )
            asteroid.add_module(Mesh, path=f"assets/meshes/asteroid_{asteroid_type}.obj")
            asteroid.add_module(Renderer)
            asteroid.renderer.texture = Texture.load_from_file(
                path="assets/textures/asteroid.png"
            )
            asteroid.add_module(
                PhysicsBody, collision_radius=asteroid.mesh.bounding_sphere_radius * 0.8
            )
            asteroid.add_module(Collider)

        # -- camera
        Scene().camera_object = GameManager().player

        while not GameManager().player.player.stop:
            EnemySpawner().update()
            EventManager().process_events()
            GraphicsBackend().next_frame()

        pygame.quit()
        sys.exit()

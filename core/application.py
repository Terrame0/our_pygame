from graphics.graphics_backend import GraphicsBackend
from graphics.texture import Texture

from core.event_manager import EventManager
from core.enemy_spawner import EnemySpawner
from core.game_manager import GameManager

from scene.modules.physics_body import PhysicsBody
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.collider import Collider

from scene.scene_object import SceneObject
from scene.scene import Scene

from pyglm import glm
from OpenGL.GL import *

from utils.singleton_decorator import singleton

import random
import pygame
import sys


@singleton
class Application:
    def __init__(self):
        EventManager()
        GraphicsBackend()
        GameManager()

    def run(self):
        for i in range(20):
            asteroid_type = glm.clamp(round(random.random() * 5), 1, 5)
            position = glm.vec3(*[random.random() - 0.5 for x in range(3)]) * 100
            scale = glm.vec3(random.random()) * 5 + 1
            rotation = glm.vec3(*[random.random() - 0.5 for x in range(3)]) * 360

            asteroid = SceneObject(
                name=f"asteroid_{asteroid_type}",
                modules=[
                    Transform(position=position, rotation=rotation, scale=scale),
                    Mesh(path=f"assets/meshes/asteroid_{asteroid_type}.obj"),
                    Renderer(
                        texture=Texture.load_from_file(
                            path="assets/textures/asteroid.png"
                        )
                    ),
                    PhysicsBody(),
                    Collider(),
                ],
            )
            asteroid.physics_body.collision_radius = (
                asteroid.mesh.bounding_sphere_radius * 0.8
            )

        # -- camera
        Scene().camera_object = GameManager().player

        while not GameManager().player.player.stop:
            EnemySpawner().update()
            EventManager().process_events()
            GraphicsBackend().next_frame()

        pygame.quit()
        sys.exit()

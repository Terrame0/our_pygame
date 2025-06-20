from core.clock import EventManager
from scene.modules.physics_body import PhysicsBody
from utils.singleton_decorator import singleton
from scene.modules.transform import Transform
from scene.modules.collider import Collider
from scene.scene_object import SceneObject
from pyglm import glm
from scene.scripts.player import Player
from scene.modules.camera import Camera
from scene.scripts.health import Health
from OpenGL.GL import *
import pygame
from utils import custom_events


@singleton
class GameManager:
    def __init__(self):
        self.enemies_alive = 0
        # -- player
        self.player = SceneObject(name="player")
        self.player.add_module(Transform, position=glm.vec3(0, 0, 10))
        self.player.add_module(Camera)
        self.player.add_module(PhysicsBody, collision_radius=0.5)
        self.player.add_module(Health, 999999)
        self.player.add_module(Player)
        self.player.add_module(Collider)

        self.score = 0

        EventManager().subscribe(custom_events.UPDATE, self.update)

    def update(self):
        pygame.display.set_caption(
            f"HEALTH: {self.player.health.value} SCORE: {self.score}"
        )
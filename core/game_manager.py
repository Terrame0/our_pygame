from core.clock import EventManager
from scene.modules.physics_body import PhysicsBody
from utils.singleton_decorator import singleton
from scene.modules.transform import Transform
from scene.modules.collider import Collider
from scene.scene_object import SceneObject
from pyglm import glm
from scene.scripts.player import Player
from scene.scripts.weapons.weapon_controller import WeaponController
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
        self.player = SceneObject(
            name="player",
            modules=[
                Transform(),
                Camera(),
                PhysicsBody(collision_radius=0.5),
                Health(999999),
                Player(),
                Collider(),
            ],
        )

        self.score = 0

        EventManager.subscribe(custom_events.UPDATE, self.update)

    def update(self):
        pygame.display.set_caption(f"HEALTH: {self.player.health.value} SCORE: {self.score}")

from graphics.graphics_backend import GraphicsBackend
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
from graphics.texture import Texture
from OpenGL.GL import *


@singleton
class Application:
    def __init__(self):
        EventManager()
        GraphicsBackend()

    def run(self):

        # -- player
        player = SceneObject(name="player")
        player.add_module(Transform, position=glm.vec3(0, 0, 5))
        player.add_module(Camera)
        player.add_module(PhysicsBody)
        player.add_module(Player)

        # -- scene object creation
        enemy = SceneObject(name="enemy")
        enemy.add_module(Transform)
        enemy.add_module(Mesh, obj_path="assets/monocarrier.obj")
        enemy.add_module(Collider)
        enemy.add_module(Renderer)
        enemy.add_module(PhysicsBody)
        enemy.add_module(Enemy, player=player)
        enemy.renderer.texture = Texture(0, "assets/monocarrier.png")
        # -- main sene
        Scene().camera_object = player

        while True:
            EventManager().process_events()
            GraphicsBackend().next_frame()

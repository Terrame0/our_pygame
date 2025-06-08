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
        cat = SceneObject(name="cat")
        cat.add_module(Transform)
        cat.add_module(Mesh, obj_path="assets/cat.obj")
        cat.add_module(Collider)
        cat.add_module(Renderer)
        cat.add_module(PhysicsBody)
        cat.add_module(Enemy, player=player)
        cat.renderer.texture = Texture(0, "assets/cat_tex.png")
        # -- main sene
        Scene().camera_object = player

        while True:
            cat.physics_body.velocity = (
                glm.vec3(
                    glm.sin(GraphicsBackend().clock.time_snapshot / 5),
                    glm.cos(GraphicsBackend().clock.time_snapshot / 5),
                    0,
                )
                * 5
            )
            EventManager().process_events()
            GraphicsBackend().next_frame()

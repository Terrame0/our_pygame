from graphics.graphics_backend import GraphicsBackend
from core.event_manager import EventManager
from utils.singleton_decorator import singleton
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.collider import Collider
from scene.scene_object import SceneObject
from scene.scene import Scene
from pyglm import glm
from core.player import Camera, Player
from graphics.texture import Texture
from OpenGL.GL import *


@singleton
class Application:
    def __init__(self):
        EventManager()
        GraphicsBackend()

    def run(self):

        # -- scene object creation
        cat = SceneObject(name="cat")
        cat.add_module(Transform)
        cat.add_module(Mesh, obj_path="assets/cat.obj")
        cat.add_module(Collider)
        cat.add_module(Renderer)
        cat.renderer.texture = Texture(0,"assets/cat_tex.png")

        # -- player
        player = Player()
        #thingie = SceneObject()
        #thingie.add_module(Transform)
        #thingie.add_module(Camera)

        # -- main sene
        Scene().camera_object = player.obj

        while True:
            EventManager().process_events()
            GraphicsBackend().next_frame()
            
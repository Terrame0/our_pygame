from graphics.graphics_backend import GraphicsBackend
from core.event_manager import EventManager
from utils.singleton_decorator import singleton
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from scene.scene import Scene
from pyglm import glm
from core.player import Player


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
        cat.add_module(Renderer)
        cat.transform.scale = glm.vec3(0.05)
        cat.transform.position = glm.vec3(0, -0.1, -0.4)

        # -- player
        player = Player()

        # -- main sene
        main_scene = Scene(camera=player.obj.camera, objects=[cat, player.obj])

        while True:
            EventManager().process_events()
            GraphicsBackend().next_frame(main_scene)
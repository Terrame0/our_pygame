from graphics.graphics_backend import GraphicsBackend
from core.event_manager import EventManager
from utils.singleton_decorator import singleton
from utils.global_variables import GVars
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from scene.scene import Scene
import glm
import time


@singleton
class Application:
    def __init__(self):
        self.event_manager = EventManager()
        self.graphics_backend = GraphicsBackend()
        self.main_scene = Scene()

        # -- scene object creation
        self.thingie = SceneObject("obj_1")
        self.thingie.add_module(Mesh)
        self.thingie.add_module(Transform, position=glm.vec3(0))
        self.thingie.add_module(Renderer)

        self.main_scene.object_list.append(self.thingie)

    def run(self):
        while True:
            self.event_manager.process_events()

            self.thingie.transform.position = glm.vec3(0, 0, -0.4)
            self.thingie.transform.scale = glm.vec3(0.2, 0.2, 0.2)
            self.thingie.transform.rotation = glm.vec3(0, glm.sin(time.time()) * 180, 0)

            self.graphics_backend.next_frame(self.main_scene)
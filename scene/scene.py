from scene.scene_object import SceneObject
from typing import List
from pyglm import glm
from scene.modules.camera import Camera
from scene.modules.transform import Transform
from utils.debug import debug


class Scene:
    def __init__(self, objects: List[SceneObject] = [], camera: Camera = None):
        debug.log(f"constructing a {self.__class__.__name__} with:")
        debug.indent()
        self.object_list: List[SceneObject] = objects
        for obj in self.object_list:
            debug.log(f"{obj.name}")
        debug.dedent()
        if camera is None:
            raise Exception(f"(!) no camera provided to {self.__class__.__name__}")
        self.camera = camera

    def add_objects(self, *objs: List[SceneObject]):
        for obj in objs:
            self.object_list.append(obj)

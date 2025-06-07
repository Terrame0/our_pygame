from __future__ import annotations
from typing import List, Type
from pyglm import glm
from scene.modules.camera import Camera
from scene.modules.transform import Transform
from utils.debug import debug
from utils.singleton_decorator import singleton


@singleton
class Scene:
    def __init__(self, objects: List = []):
        self._camera_object = None
        debug.log(f"constructing a {self.__class__.__name__} with:")
        debug.indent()
        self.object_list: List = objects
        for obj in self.object_list:
            debug.log(f"{obj.name}")
        debug.dedent()

    def add_objects(self, *objs: List):
        for obj in objs:
            self.object_list.append(obj)

    @property
    def camera(self):
        if self._camera_object is None:
            raise Exception(f"(!) {self.__class__.__name__} has no camera provided")
        return self._camera_object.camera

    @property
    def camera_object(self):
        if self._camera_object is None:
            raise Exception(f"(!) {self.__class__.__name__} has no camera provided")
        return self._camera_object

    @camera_object.setter
    def camera_object(self, camera_object):
        if not hasattr(camera_object, "camera"):
            raise Exception(f"(!) provided camera object has no camera module")

        self._camera_object = camera_object
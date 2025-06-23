from __future__ import annotations
from typing import List
from utils.debug import debug
from utils.singleton_decorator import singleton


@singleton
class Scene:
    def __init__(self):
        self._camera_object = None
        self.objects: List = []

    def add_objects(self, *objs: List):
        for obj in objs:
            self.objects.append(obj)

    def remove_objects(self, *objs: List):
        for obj in objs:
            self.objects.remove(obj)

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
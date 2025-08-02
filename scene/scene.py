from __future__ import annotations
from utils.singleton_decorator import singleton

from OpenGL.GL import *


@singleton
class ObjectIDManager:
    def __init__(self):
        self.id_queue_pointer = 0
        self.id_queue = [x for x in range(Scene.MAX_OBJECTS)]

    def get_id(self):
        if self.id_queue_pointer >= Scene.MAX_OBJECTS:
            raise RuntimeError(f"(!) object ID pool exhausted!")
        out = self.id_queue[self.id_queue_pointer]
        self.id_queue[self.id_queue_pointer] = -1
        self.id_queue_pointer += 1
        return out

    def return_id(self, idx: int):
        self.id_queue_pointer -= 1
        self.id_queue[self.id_queue_pointer] = idx


@singleton
class Scene:

    MAX_OBJECTS = 10000

    def __init__(self):
        self._camera_object = None
        self.objects = []

    def add_object(self, obj) -> int:  # -- returns object id
        self.objects.append(obj)
        return ObjectIDManager.get_id()

    def remove_object(self, obj):
        ObjectIDManager.return_id(obj.id)
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

from scene.scene_object import SceneObject
from typing import List


class Scene:
    def __init__(self):
        self.object_list: List[SceneObject] = []
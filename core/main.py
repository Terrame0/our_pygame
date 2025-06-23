from core.application import Application

from scene.scene_object import SceneObject
from scene.modules.camera import Camera
from scene.modules.transform import Transform
from pyglm import glm

from utils.debug import debug


def fun(a, b):
    print(a, b)


if __name__ == "__main__":

    app = Application()
    app.run()
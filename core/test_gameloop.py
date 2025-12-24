
import random
from pyglm import glm
import ctypes
import sdl2 as sdl

from graphics.graphics_backend import GraphicsBackend
from graphics.loaders.shader_loader import ShaderLoader

from core.event_manager import EventManager

from scene.modules.renderer import Renderer
from scene.modules.transform import Transform
from scene.modules.camera import Camera
from scene.modules.physics_body import PhysicsBody
from scene.modules.new_collider import NewCollider

from scene.scripts.camera_controller import CameraController

# from scene.scripts.player import Player
from scene.scripts.health import Health

from scene.gizmos.bounding_box import AABB
from graphics.bvh import BVH
from utils.tree_printer import TreePrinter, TreeVisualizer

from scene.scene_object import SceneObject
from scene.scene import Scene
from core.clock import Clock

from utils.singleton_decorator import singleton
from utils.debug import debug


def inv_cdf(value: float):
    return glm.sqrt(value)
    return glm.acos(2 * value - 1) / glm.pi()


@singleton
class TestGameloop:
    def __init__(self):

        GraphicsBackend.init()

        Scene.camera_object = SceneObject(
            name=f"viewer",
            modules=[
                Transform(position=glm.vec3(0, 0, 5)),
                Camera,
                CameraController,
            ],
        )

        objs = [
            SceneObject(
                name=f"test_{i}",
                modules=[
                    Transform,
                    Renderer(mesh="cat.obj", texture="cat_tex.png", is_transparent=False),
                    NewCollider,
                ],
            )
            for i in range(10)
        ]

        while True:
            for i, obj in enumerate(objs):
                # obj.transform.rotation = glm.vec3((Clock.now - Clock.start_time) * 10)

                obj.transform.position = (
                    glm.vec3(
                        glm.sin(Clock.now / 1000 * (i)),
                        glm.cos(Clock.now / 1000 * (i * 2)),
                        glm.cos(Clock.now / 1000 * (i * 3)),
                    )
                    * (i + 1)
                    * 5
                )
            # TreePrinter.print(Scene.bvh.root)
            TreeVisualizer.draw(Scene.bvh.root)

            EventManager.process_events()
            GraphicsBackend.next_frame()

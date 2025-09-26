
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
                    Transform(position=glm.vec3(0, 0, 0)),
                    Renderer(mesh="sphere.obj", texture="blue.png", is_transparent=False),
                    NewCollider,
                ],
            )
            for i in range(2)
        ]

        # spawn_time = Clock.now
        # counter = 0
        # leaves = []
        # max_count = 100
        while True:
            for i, obj in enumerate(objs):
                # obj.transform.rotation = glm.vec3((Clock.now - Clock.start_time) * 10)

                obj.transform.position = (
                    glm.vec3(glm.sin(Clock.now * (i+1)), 0, glm.cos(Clock.now * (i+1))) * (i+1)
                )

            # bnuy.transform.rotation = glm.vec3((glm.sin(Clock.now / 2) + 1) / 2 * 360)

            # bnuy.transform.position = glm.vec3((glm.sin(Clock.now / 2) + 1) / 2) * 3
            # bnuy.transform.scale = glm.vec3(((glm.sin(Clock.now * 10) + 1) / 2) * 0.2 + 1)

            # if Clock.now - spawn_time > 0.1:
            #     spawn_time = Clock.now
            #     counter += 1
            #     if counter < max_count:
            #         random.seed(counter)
            #         pos = glm.vec3(
            #             random.random(),
            #             random.random(),
            #             random.random(),
            #         )
            #         size = glm.vec3(
            #             random.random(),
            #             random.random(),
            #             random.random(),
            #         )
            #
            #         aabb = AABB(pos * 50, pos * 50 + size + 0.1)
            #
            #         leaves.append(bvh.insert(aabb))
            #         TreeVisualizer.draw(bvh.root)

            EventManager.process_events()
            GraphicsBackend.next_frame()

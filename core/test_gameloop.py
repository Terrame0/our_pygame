from OpenGL.GL import *

from pyglm import glm

from graphics.graphics_backend import GraphicsBackend
from graphics.loaders.shader_loader import ShaderLoader

from core.event_manager import EventManager

from scene.modules.renderer import Renderer
from scene.modules.transform import Transform
from scene.modules.camera import Camera
from scene.modules.physics_body import PhysicsBody

from scene.scripts.player import Player
from scene.scripts.health import Health

from scene.scene_object import SceneObject
from scene.scene import Scene
from core.clock import Clock

from utils.singleton_decorator import singleton


from OpenGL.GL import *


@singleton
class TestGameloop:
    def __init__(self):
        GraphicsBackend.init()

        Scene.camera_object = SceneObject(
            name=f"viewer",
            modules=[
                Transform(position=glm.vec3(0, 0, 15)),
                Camera,
                PhysicsBody(collision_radius=0.5),
                Health(100),
                Player,
            ],
        )

        grid_size = glm.uvec3(1)

        for x in range(-grid_size.x, grid_size.x + 1):
            for y in range(-grid_size.y, grid_size.y + 1):
                for z in range(-grid_size.z, grid_size.z + 1):
                    position = glm.vec3(x, y, z) * 3
                    SceneObject(
                        name=f"test_transparent",
                        modules=[
                            Transform(position=position),
                            Renderer(
                                mesh="plane.obj",
                                texture=f"""plasma{"_red" if (x+y+z+round(Clock.now))%2==0 else ""}.png""",
                                is_transparent = True,
                            ),
                        ],
                    )

        a = SceneObject(
            name=f"test_opaque",
            modules=[
                Transform(position=position),
                Renderer(
                    mesh="cube.obj",
                    texture=f"cat_tex.png",
                    is_transparent = False,
                ),
            ],
        )

        while True:
            a.renderer.is_visible = True
            EventManager.process_events()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            GraphicsBackend.next_frame()

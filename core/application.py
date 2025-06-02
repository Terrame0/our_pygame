from graphics.graphics_backend import GraphicsBackend
from utils import custom_events
from core.event_manager import EventManager
from utils.singleton_decorator import singleton
from utils.global_variables import GVars
from scene.modules.mesh import Mesh
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.scene_object import SceneObject
from scene.modules.camera import Camera
from scene.scene import Scene
import pygame
from pyglm import glm
import time
from graphics.clock import Clock
from utils.debug import debug


class Player:
    def __init__(self):
        self.obj = SceneObject(name="player")
        self.obj.add_module(Transform)
        self.obj.add_module(Camera)

        EventManager().subscribe(pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False)
        EventManager().subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)

        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        EventManager().subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

        EventManager().subscribe(custom_events.UPDATE, self.wasd_move)
        EventManager().subscribe(pygame.MOUSEMOTION, self.look_around)

    def wasd_move(self):
        d = glm.vec3(0)
        needs_update = False
        for key, vec in {
            pygame.K_w: glm.vec3(0, 0, -1),
            pygame.K_a: glm.vec3(-1, 0, 0),
            pygame.K_s: glm.vec3(0, 0, 1),
            pygame.K_d: glm.vec3(1, 0, 0),
            pygame.K_LCTRL: glm.vec3(0, -1, 0),
            pygame.K_SPACE: glm.vec3(0, 1, 0),
        }.items():
            if pygame.key.get_pressed()[key]:
                needs_update = True
                d += vec
                # debug.log(f"pressed {key} with vec {vec}")
        clock = GraphicsBackend().clock
        if needs_update and d != glm.vec3(0):
            # debug.log(d)
            self.obj.transform.position = (
                self.obj.transform.position
                + self.obj.transform.R * glm.normalize(d) * clock.delta_time
            )

    def look_around(self):
        mpos = pygame.mouse.get_rel()
        # debug.log(mpos)
        clock = GraphicsBackend().clock
        self.obj.transform.rotation = (
            self.obj.transform.rotation
            + glm.vec3(-mpos[1], -mpos[0], 0) * clock.delta_time * 1000
        )


@singleton
class Application:
    def __init__(self):
        EventManager()
        GraphicsBackend()

    def run(self):

        # -- scene object creation
        cat = SceneObject(name="cat")
        cat.add_module(Transform, position=glm.vec3(0))
        cat.add_module(Mesh)
        cat.add_module(Renderer)
        cat.transform.scale = glm.vec3(0.05)
        cat.transform.position = glm.vec3(0, -0.1, -0.4)

        # -- player
        player = Player()

        # -- main sene
        main_scene = Scene(camera=player.obj.camera, objects=[cat, player.obj])

        while True:
            EventManager().process_events()
            GraphicsBackend().next_frame(main_scene)
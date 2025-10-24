from __future__ import annotations

import OpenGL
import sdl2 as sdl

OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from utils.singleton_decorator import singleton
from graphics.geometry_renderer import GeometryRenderer
from graphics.blitter import Blitter
from graphics.window import Window


@singleton
class GraphicsBackend:

    def __init__(self):
        self.init_state()

    def init_state(self):
        # -- window creation
        
        Window.init(1000, 1000)

        # -- global opengl state
        # glEnable(GL_FRAMEBUFFER_SRGB)
        # glClearColor(0.2, 0.2, 0.2, 0.0)
        glClearColor(1, 1, 1, 0.0)
        # glClearColor(0.53, 0.81, 0.98, 0.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glLineWidth(5)

    def next_frame(self):

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        Blitter.blit_to_screen(
            GeometryRenderer.draw(),
        )

        # ParticleSystem.reset_particles()

        Window.flip()

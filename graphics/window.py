from typing import Tuple

from core.event_manager import EventManager

from utils.singleton_decorator import singleton
from utils.debug import debug

import pygame
from OpenGL.GL import *


@singleton
class Window:

    def __init__(self, width: int, height: int):
        self.size = (width, height)
        pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.OPENGL)
        EventManager.subscribe(pygame.VIDEORESIZE, self.resize, pass_event=True)
        # EventManager.subscribe(pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False)
        # EventManager.subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)
        # EventManager.subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        # EventManager.subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

    def resize(self, event):
        self.size = event.size

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def aspect_ratio(self):
        return self.width / self.height

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: Tuple[int]):
        self._size = size
        debug.log(f"window size: {self._size}")
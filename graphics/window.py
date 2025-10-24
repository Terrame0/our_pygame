from typing import Tuple

from core.event_manager import EventManager

from utils.singleton_decorator import singleton
from utils.debug import debug

from OpenGL.GL import *
import sdl2 as sdl


@singleton
class Window:

    def __init__(self, width: int, height: int):
        self.size = (width, height)
        sdl.SDL_Init(sdl.SDL_INIT_EVERYTHING)
        self.window = sdl.SDL_CreateWindow(
            b"OpenGL Example",
            sdl.SDL_WINDOWPOS_CENTERED,
            sdl.SDL_WINDOWPOS_CENTERED,
            self.size[0],
            self.size[1],
            sdl.SDL_WINDOW_OPENGL | sdl.SDL_WINDOW_SHOWN,
        )
        self.gl_context = sdl.SDL_GL_CreateContext(self.window)
        sdl.SDL_GL_SetAttribute(sdl.SDL_GL_DOUBLEBUFFER, 1)
        sdl.SDL_GL_SetSwapInterval(0)

        # pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.OPENGL)
        # EventManager.subscribe(pygame.VIDEORESIZE, self.resize, pass_event=True)
        # EventManager.subscribe(pygame.WINDOWFOCUSGAINED, pygame.mouse.set_visible, False)
        # EventManager.subscribe(pygame.WINDOWFOCUSGAINED, pygame.event.set_grab, True)
        # EventManager.subscribe(pygame.WINDOWFOCUSLOST, pygame.mouse.set_visible, True)
        # EventManager.subscribe(pygame.WINDOWFOCUSLOST, pygame.event.set_grab, False)

    # def __del__(self):
    #     sdl.SDL_GL_DeleteContext(self.gl_context)
    #     sdl.SDL_DestroyWindow(self.window)
    #     sdl.SDL_Quit()

    def flip(self):
        sdl.SDL_GL_SwapWindow(self.window)

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
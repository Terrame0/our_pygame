import sdl2 as sdl
import ctypes
import glm

from core.event_manager import EventManager
from core.event_system.user_events import UserEvents

from utils.singleton_decorator import singleton


@singleton
class UserInput:

    def __init__(self):
        self._needs_update = True
        self._cx = ctypes.c_int(0)
        self._cy = ctypes.c_int(0)
        self.update()
        EventManager.subscribe(UserEvents["update"], self.update)

    def update(self):
        self._mbutton_state = sdl.SDL_GetMouseState(ctypes.byref(self._cx), ctypes.byref(self._cy))
        self._keyboard_state = sdl.SDL_GetKeyboardState(None)

    @property
    def mpos(self) -> glm.ivec2:
        return glm.ivec2(
            int(self._cx.value),
            int(self._cy.value),
        )

    def mbutton(self, button_index: int) -> bool:
        mask = 1 << (button_index - 1)
        return bool(self._mbutton_state & mask)

    def key(self, scancode: int) -> bool:
        return bool(self._keyboard_state[scancode])
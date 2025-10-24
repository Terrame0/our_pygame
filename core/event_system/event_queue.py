from utils.singleton_decorator import singleton
import sdl2 as sdl
import ctypes
from core.event_system.user_events import UserEvents


@singleton
class EventQueue:

    def poll_events(self):
        event = sdl.SDL_Event()
        while sdl.SDL_PollEvent(ctypes.byref(event)) != 0:
            yield event

    def __init__(self):
        pass
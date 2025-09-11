import ctypes
import sdl2 as sdl
from utils.singleton_decorator import singleton


class UserEventInstance(sdl.SDL_Event):

    def post(self, payload=None):
        if payload is not None:
            self.user.data1 = ctypes.cast(
                ctypes.pointer(ctypes.py_object(payload)), ctypes.c_void_p
            )
        sdl.SDL_PushEvent(ctypes.byref(self))

    def __init__(self, evt_type):
        super().__init__()
        self.type = evt_type
        self.user.type = evt_type


@singleton
class UserEvents:

    event_type_registry = {}

    def __init__(self):
        self.register_event("update")

    def register_event(self, name):
        self.event_type_registry[name] = sdl.SDL_RegisterEvents(1)

    def process_event(self, event):
        ptr = ctypes.cast(event.user.data1, ctypes.POINTER(ctypes.py_object))
        return ptr.contents.value

    def get_id(self, name):
        return self.event_type_registry[name]

    def get_instance(self, name):
        return UserEventInstance(self.get_id(name))
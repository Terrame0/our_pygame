import ctypes
import sdl2 as sdl
from utils.singleton_decorator import singleton


class Payload:
    def __init__(self, **kwargs):
        for name, arg in kwargs.items():
            setattr(self, name, arg)


class UserEventInstance(sdl.SDL_Event):
    payload_registry = {}

    def post(
        self,
        **kwargs,
    ):
        payload = Payload(**kwargs)
        pyobj = ctypes.py_object(payload)
        self.payload_registry[id(payload)] = pyobj
        self.user.data1 = ctypes.cast(ctypes.pointer(pyobj), ctypes.c_void_p)
        return sdl.SDL_PushEvent(ctypes.byref(self))

    def __init__(self, evt_type):
        super().__init__()
        self.type = evt_type
        self.user.type = evt_type


@singleton
class UserEvents:

    event_type_registry = {}

    def __init__(self):
        self.register_event("update")

    def register_event(self, name) -> int:
        assigned_id = sdl.SDL_RegisterEvents(1)
        if assigned_id != 2**32 - 1:
            self.event_type_registry[name] = assigned_id
            return assigned_id
        else:
            raise RuntimeError(f"(!) {name} event initialization failed")

    def get_payload(self, event):
        if event.type in self.event_type_registry.values():
            try:
                ptr = ctypes.cast(event.user.data1, ctypes.POINTER(ctypes.py_object))
                payload = ptr.contents.value
            except:
                raise RuntimeError(
                    f"(!) error trying to dereference the payload pointer for {event.type}"
                )
            if id(payload) in UserEventInstance.payload_registry:
                del UserEventInstance.payload_registry[id(payload)]
                return payload
            else:
                raise RuntimeError(f"(!) payload {payload} for  has already been retrieved")
        else:
            return None

    def free_payload(self, payload):
        del UserEventInstance.payload_registry[id(payload)]

    # -- an alias for get_type()
    def __getitem__(self, name) -> int:
        return self.get_type(name)

    def get_type(self, name) -> int:
        return self.event_type_registry[name]

    def get_instance(self, name) -> UserEventInstance:
        return UserEventInstance(self.get_type(name))
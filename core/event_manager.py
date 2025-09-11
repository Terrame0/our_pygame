from utils.singleton_decorator import singleton
from typing import Callable, Any
from collections import defaultdict
from utils.debug import debug

import sys
import sdl2 as sdl
import ctypes

from core.event_system.user_events import UserEvents, UserEventInstance
from core.event_system.event_queue import EventQueue


@singleton
class EventManager:
    asdf = 1

    def __init__(self):
        self.subscriptions = defaultdict(list)

    def subscribe(
        self,
        event_type: Any,
        callback: Callable[[Any], None],
        *args: Any,
        **kwargs: Any,
    ):
        parameters = {"pass_event": None}
        for name in parameters.keys():
            if name in kwargs:
                parameters[name] = kwargs[name]
                del kwargs[name]
        self.subscriptions[event_type].append((callback, (args, kwargs), parameters))

        debug.log(f"subscribed callback to {event_type}")

    def unsubscribe(self, event_type: Any, callback: Callable):
        if event_type in self.subscriptions:
            original_subscriptions = self.subscriptions[event_type][:]

            for entry in original_subscriptions:
                if entry[0] == callback:
                    self.subscriptions[event_type].remove(entry)
                    debug.log(f"unsubscribed callback from {event_type}")
                    return
            raise RuntimeError(f"(!) callback not found for {event_type}")
        else:
            raise RuntimeError(f"(!) event_type {event_type} not found in subscriptions")

    def emit(self, event: Any):
        if event.type in self.subscriptions:
            for entry in self.subscriptions[event.type]:
                try:
                    callback, (args, kwargs), parameters = entry
                    if parameters["pass_event"] is True:
                        callback(event, *args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    raise RuntimeError(f"(!) error in callback for {event}, {callback}: {str(e)}")

    def process_events(self):
        UserEvents.get_instance("update").post()
        event = sdl.SDL_Event()
        for event in EventQueue.poll_events():
            if event.type == sdl.SDL_QUIT:
                sys.exit()
            self.emit(event)

from utils.singleton_decorator import singleton
from typing import DefaultDict, Callable, Any, List, Tuple, Type
from collections import defaultdict
from utils.debug import debug
import pygame


@singleton
class EventManager:
    def __init__(self):
        self._subscriptions = defaultdict(list)

    def subscribe(
        self,
        event_type: Any,
        f: Callable[[pygame.event.Event, Any], None] = None,
        *args: Any,
        **kwargs: Any,
    ):
        self._subscriptions[event_type].append({"callable": f, "data": (args, kwargs)})
        debug.log(f"subscribed callback to {event_type}")

    def unsubscribe(self, event_type: Any, callback: Callable):
        if event_type in self._subscriptions:
            original_subscriptions = self._subscriptions[event_type][:]
            removed = False

            for subscription in original_subscriptions:
                if subscription["callable"] == callback:
                    self._subscriptions[event_type].remove(subscription)
                    removed = True
                    debug.log(f"unsubscribed callback from {event_type}")

            if not removed:
                debug.log(f"(*) callback not found for {event_type}")
        else:
            debug.log(f"event_type {event_type} not found in subscriptions")

    def emit(self, event: Any):
        if event.type in self._subscriptions:
            for callback in self._subscriptions[event.type]:
                try:
                    args = callback["data"][0][:]
                    kwargs = callback["data"][1].copy()
                    if "pass_event" in kwargs:
                        if kwargs["pass_event"] == True:
                            args = (event, *args)
                        del kwargs["pass_event"]

                    callback["callable"](*args, **kwargs)

                except Exception as e:
                    debug.log(f"error in callback for {event.type}: {str(e)}")

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            self.emit(event)
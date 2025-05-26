from utils.singleton_decorator import singleton
from typing import defaultdict
from utils.debug import debug
import pygame


@singleton
class EventManager:
    def __init__(self):
        self._subscriptions = defaultdict(list)

    def subscribe(self, event_type, handler):
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if event_type in self._subscriptions:
            self._subscriptions[event_type].remove(handler)

    def emit(self, event_type, data=None):
        if event_type in self._subscriptions:
            for handler in self._subscriptions[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    debug.log(f"error in handler for {event_type}: {str(e)}")

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            self.emit(event.type)
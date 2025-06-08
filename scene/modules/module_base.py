from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type, List, Any, Callable
from utils.debug import debug
from core.event_manager import EventManager


class Module(ABC):
    requires: List[Type[Module]] = []

    # -- functions as the constructor for subclasses
    @abstractmethod
    def __init_module__(self, *args, **kwargs):
        pass

    def __init__(self, obj, *args, **kwargs):
        debug.log(f"constructing a {self.__class__.__name__} module")

        self.event_subscriptions = []

        # -- module list validity check
        if obj is not None:
            self.parent_obj = obj
        else:
            raise Exception(
                f"(!) no parent object provided to {self.__class__.__name__} module constructor"
            )

        # -- calling the child's constructor
        self.__init_module__(*args, **kwargs)

        # -- checking requirements
        missing = [
            req.__name__
            for req in self.requires
            if req.__name__ not in self.parent_obj.modules
        ]
        if missing:
            raise Exception(
                f"(!) missing required modules for {self.__class__.__name__}: {', '.join(missing)}"
            )

    def subscribe_to_event(
        self,
        event_type: Any,
        callback: Callable[[Any], None] = None,
        *args: Any,
        **kwargs: Any,
    ):
        EventManager().subscribe(event_type, callback, *args, **kwargs)
        self.event_subscriptions.append((event_type, callback))

    def deinit(self):
        for subscription in self.event_subscriptions:
            EventManager().unsubscribe(subscription[0], subscription[1])

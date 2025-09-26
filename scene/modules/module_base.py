from __future__ import annotations
from abc import ABC, ABCMeta, abstractmethod
from typing import Type, List, Any, Callable
from utils.debug import debug
from core.event_manager import EventManager
from utils.case_converter import pascal_to_snake
from utils.classproperty import classproperty
from core.event_system.user_events import UserEvents


# -- metaclass to precompute class names
class ModuleMeta(ABCMeta):
    def __new__(cls, name, bases, namespace):
        namespace["name_snake"] = pascal_to_snake(name)
        namespace["name_pascal"] = name
        namespace["__str__"] = cls.__str__
        if "local_events" in namespace:
            event_types = []
            for event_name in namespace["local_events"]:
                event_types.append(UserEvents.register_event(event_name))
            namespace["local_events"] = dict(zip(namespace["local_events"], event_types))
        return super().__new__(cls, name, bases, namespace)

    def __str__(self):
        return f"[{self.name_pascal}]"


class Module(ABC, metaclass=ModuleMeta):
    requires: List[Module] = []
    local_events: List[str] = (
        []
    )  # -- gets changed to a dictionary of event name/type pairs after initialization

    def __init__(self, *args, **kwargs):
        self.event_subscriptions = []
        self.construction_args = (args, kwargs)  # -- storing arguments for lazy construction

    # -- functions as the constructor for subclasses
    @abstractmethod
    def __init_module__(self, *args, **kwargs):
        pass

    # -- raises an error if no reference is available
    @property
    def parent_obj(self):
        if self._parent_obj is not None:
            return self._parent_obj
        else:
            raise Exception(
                f"(!) module [{self.name_pascal}] is missing a parent object reference (probably isn't bound to any)"
            )

    # == functions as a lazy constructor
    # -- sets parent object reference, adds the module to the
    # -- parent object module list, then calls the constructor
    @parent_obj.setter
    def parent_obj(self, parent_obj):
        debug.log(f"attaching [{self.name_pascal}] module to {parent_obj}")

        if self not in parent_obj.modules:
            self._parent_obj = parent_obj
            self.check_required_modules(parent_obj)  # -- checking module dependencies
            parent_obj.modules[self.name_snake] = self  # -- adding self to modules
            self.__init_module__(*self.construction_args[0], **self.construction_args[1])
        else:
            debug.log(f"(*) [{self.name_pascal}] module is already attached to {parent_obj}!")

    def check_required_modules(self, parent_obj):
        missing = [
            required_module.name_snake
            for required_module in self.requires
            if required_module.name_snake not in parent_obj.modules
        ]
        if missing:
            raise Exception(
                f"(!) missing required modules on {parent_obj} for [{self.name_pascal}] module: {', '.join(missing)}"
            )

    def post_event(self, name, **kwargs):
        UserEvents.get_instance(name).post(**kwargs, progenitor=self.parent_obj)

    def subscribe_to_event(
        self,
        event_type: Any,
        callback: Callable[[Any], None] = None,
        *args: Any,
        **kwargs: Any,
    ):
        EventManager.subscribe(event_type, callback, *args, **kwargs)
        self.event_subscriptions.append((event_type, callback))

    def deinit_base(self):
        for event_type, callback in self.event_subscriptions:
            EventManager.unsubscribe(event_type, callback)

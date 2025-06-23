from __future__ import annotations
from abc import ABC, ABCMeta, abstractmethod
from typing import Type, List, Any, Callable
from utils.debug import debug
from core.event_manager import EventManager
from utils.case_converter import pascal_to_snake
from utils.classproperty import classproperty


# -- metaclass to precompute class names
class ModuleMeta(ABCMeta):
    def __new__(cls, name, bases, namespace):
        namespace["name_snake"] = pascal_to_snake(name)
        namespace["name_pascal"] = name
        return super().__new__(cls, name, bases, namespace)


class Module(ABC, metaclass=ModuleMeta):
    requires: List[Type[Module]] = []

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
            # -- checking requirements
            missing = [
                required_module.name_snake
                for required_module in self.requires
                if required_module.name_snake not in parent_obj.modules
            ]
            if missing:
                raise Exception(
                    f"(!) missing required modules on {parent_obj} for [{self.name_pascal}] module: {', '.join(missing)}"
                )

            parent_obj.modules[self.name_snake] = self  # -- adding self to modules
            self.__init_module__(*self._args[0], **self._args[1])
        else:
            debug.log(
                f"(*) [{self.name_pascal}] module is already attached to {parent_obj}!"
            )

    def __init__(self, *args, **kwargs):
        debug.log(f"instantiating [{self.name_pascal}] module")
        self._event_subscriptions = []
        self._args = (args, kwargs)  # -- storing arguments for lazy construction

    def subscribe_to_event(
        self,
        event_type: Any,
        callback: Callable[[Any], None] = None,
        *args: Any,
        **kwargs: Any,
    ):
        EventManager().subscribe(event_type, callback, *args, **kwargs)
        self._event_subscriptions.append((event_type, callback))

    def deinit_base(self):
        for subscription in self._event_subscriptions:
            EventManager().unsubscribe(subscription[0], subscription[1])

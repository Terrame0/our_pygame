from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type, List
from utils.debug import debug


class Module(ABC):
    requires: List[Type[Module]] = []

    def __init__(self, parent, *args, **kwargs):
        debug.log(f"constructing a {self.__class__.__name__} module")

        # -- module list validity check
        if parent is not None:
            self.parent = parent
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
            if req.__name__ not in self.parent.modules
        ]
        if missing:
            raise Exception(
                f"(!) missing required modules for {self.__class__.__name__}: {', '.join(missing)}"
            )

    # -- functions as the constructor for subclasses
    @abstractmethod
    def __init_module__(self, *args, **kwargs):
        pass
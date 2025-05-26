from abc import ABC, abstractmethod
from typing import Dict, Type, List
from utils.debug import debug


class Module(ABC):
    requires: List[Type["Module"]] = []

    def __init__(self, *args, module_list: Dict[str, "Module"] = None, **kwargs):
        debug.log(f"constructing a {self.__class__.__name__} module")

        # -- module list validity check
        if module_list is not None:
            self.parent_modules = module_list
        else:
            raise Exception(
                f"(!) no parent module list provided to {self.__class__.__name__} module constructor"
            )

        # -- checking requirements
        missing = [
            req.__name__
            for req in self.requires
            if req.__name__ not in self.parent_modules
        ]
        if missing:
            raise Exception(
                f"(!) missing required modules for {self.__class__.__name__}: {', '.join(missing)}"
            )

        self.__init_module__(*args, **kwargs)

    # -- functions as the constructor for subclasses
    @abstractmethod
    def __init_module__(self, *args, **kwargs):
        pass
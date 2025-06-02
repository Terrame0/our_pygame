from scene.modules.module_base import Module
from typing import Dict, Type
from utils.debug import debug


class SceneObject:
    def __init__(self, name: str = "default"):
        self.module_list: Dict[str, Module] = {}
        self.name = name
        debug.log(f"consturcting a {self.__class__.__name__} {self.name}")

    def __getattr__(self, module_name: str):
        module_name = module_name.capitalize()
        if module_name in self.module_list:
            return self.module_list[module_name]
        else:
            raise AttributeError(
                f"(!) no module {module_name} attached to {self.__class__.__name__} {self.name}"
            )

    def add_module(self, module_type: Type[Module], *args, **kwargs) -> Module:
        module_name = module_type.__name__
        if module_type not in self.module_list:
            debug.log(f"attaching a {module_name} module to {self.__class__.__name__}")
            self.module_list[module_name] = module_type(
                *args, module_list=self.module_list, **kwargs
            )
        else:
            debug.log(
                f"(*) module {module_name} is already attached to {self.__class__.__name__} {self.name}!"
            )
        return self.module_list[module_name]

    def __str__(self):
        return self.name

    def remove_module(self, module_type: Type[Module]):
        module_name = module_type.__name__
        debug.log(f"removing {module_name} from {self.__class__.__name__} {self.name}")
        del self.module_list[module_name]
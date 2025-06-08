from __future__ import annotations
from scene.modules.module_base import Module
from typing import Dict, Type
from utils.debug import debug
from scene.scene import Scene
from utils.snake_to_pascal import snake_to_pascal


class SceneObject:
    def __init__(self, name: str = "default"):
        Scene().add_objects(self)
        self.modules: Dict[str, Module] = {}
        self.name = name
        debug.log(f"consturcting a {self.__class__.__name__} {self.name}")

    def __getattr__(self, module_name: str):
        module_name = snake_to_pascal(module_name)
        if module_name in self.modules:
            return self.modules[module_name]
        else:
            raise AttributeError(
                f"(!) no module {module_name} attached to {self.__class__.__name__} {self.name}"
            )

    def add_module(self, module_type: Type[Module], *args, **kwargs) -> Module:
        module_name = module_type.__name__
        if module_type not in self.modules:
            debug.log(f"attaching a {module_name} module to {self.__class__.__name__}")
            self.modules[module_name] = module_type(self, *args, **kwargs)
        else:
            debug.log(
                f"(*) module {module_name} is already attached to {self.__class__.__name__} {self.name}!"
            )
        return self.modules[module_name]

    def __repr__(self):
        return self.name

    def remove_module(self, module_type: Type[Module]):
        module_name = module_type.__name__
        debug.log(f"removing {module_name} from {self.__class__.__name__} {self.name}")
        del self.modules[module_name]

    def destroy(self):
        Scene().remove_objects(self)
        for module in self.modules.values():
            if hasattr(module, "deinit"):
                module.deinit()
        debug.log(f"destroyed {self.__class__.__name__} {self.name}")
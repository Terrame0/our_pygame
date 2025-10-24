from __future__ import annotations
from scene.modules.module_base import Module
from typing import Dict, Type, List
from utils.debug import debug
from scene.scene import Scene


class SceneObject:
    def __init__(self, modules: List[Module] = [], name: str = "default"):
        self.id = Scene.add_object(self)
        self.name = name
        debug.log(
            f"""constructing {"a" if modules else "an empty"} {self} {"with:" if modules else ""}"""
        )
        self.modules: Dict[str, Module] = {}
        if modules:
            debug.indent()
            for module in modules:
                debug.log(module)
                debug.disable
                self.add_module(module)
                debug.enable
            debug.dedent()

    def __getattr__(self, module_name: str):
        if module_name in self.modules:
            return self.modules[module_name]
        else:
            raise AttributeError(f"(!) no [{module_name}] module attached to {self}")

    def __repr__(self):
        return f"[{self.__class__.__name__}] [{self.id}] ({self.name}) "

    def add_module(self, module: Module | Type[Module]) -> None:
        try:
            if issubclass(module, Module):  # -- if module is a type
                module = module()  # -- set it to an instance of said type
        except TypeError:
            pass
        module.parent_obj = self

    def remove_module(self, module: Module):
        debug.log(f"removing {module.name_pascal} from {self}")
        if module in self.modules.values():
            module.deinit_base()
            if hasattr(module, "deinit"):
                module.deinit()
            del self.modules[module.name_snake]
        else:
            debug.log(f"(*) no {module.name_pascal} module attached to {self}")

    def has_module(self, module_name: str) -> bool:
        return module_name in self.modules

    def destroy(self):
        debug.log(f"destroying {self}")
        Scene.remove_object(self)
        modules_to_remove = list(self.modules.values())  # -- creating a copy
        for module in modules_to_remove:
            self.remove_module(module)

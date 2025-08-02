from __future__ import annotations
from abc import ABC, ABCMeta, abstractmethod
from typing import Dict

class MaterialMeta(ABCMeta):
    def __new__(cls, name, bases, namespace):
        if "shaders" in namespace and isinstance(namespace["shaders"],dict):
            shaders = namespace["shaders"]
            for shader_type,path in shaders:
                print(shader_type,path)
        return super().__new__(cls, name, bases, namespace)

class Material(ABC, metaclass = MaterialMeta):
    shaders: Dict[int,str] = {}

    def __init__(self):
        pass

    @abstractmethod
    def __init_material__(self):
        pass

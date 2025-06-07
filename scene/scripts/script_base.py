from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type, List
from utils.debug import debug
from scene.modules.module_base import Module


class Script(Module):
    def __init_module__(self):
        self.subscription_list = []
        self.__init_script__()

    @abstractmethod
    def __init_script__(self, *args, **kwargs):
        pass
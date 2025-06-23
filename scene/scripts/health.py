from scene.modules.module_base import Module


class Health(Module):
    def __init_module__(self, initial_value:int):
        self.value = initial_value
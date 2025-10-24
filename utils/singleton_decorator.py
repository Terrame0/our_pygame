from utils.debug import debug
import inspect


def singleton(cls):
    instances = {}

    class SingletonWrapper(cls):

        # -- dummy-plugging __init__ so that parent class
        # -- default constructor isn't called automatically
        def __init__(self):
            self._initialized = False
            self.__class__.__name__ = cls.__name__

        def __new__(_cls):
            if cls not in instances:
                # -- bypasses overloaded __new__, avoids infinite recursion
                instances[cls] = object.__new__(_cls)
            return instances[cls]

        # -- a function for delayed construction
        def init(self, *args, **kwargs):
            if not self._initialized:
                self._initialized = True
                debug.log(f"initializing {self}")
                super().__init__(*args, **kwargs)
            else:
                debug.log(f"(*) {self} is already initialized!")

        # -- getattribute calls init() if the singleton
        # -- is uninitialized and an attribute is accessed
        def __getattribute__(self, name):
            if name == "_initialized" or name == "init" or name.startswith("__"):
                return object.__getattribute__(self, name)
            elif not object.__getattribute__(self, "_initialized"):
                if len(inspect.signature(super().__init__).parameters) == 0:
                    self.init()
                else:
                    raise RuntimeError(f"(!) {self} has to be initialized manually!")
            return super().__getattribute__(name)

        def __str__(self):
            return f"[{self.__class__.__name__}] singleton"

    return SingletonWrapper()


# def singleton(cls):
#    instances = {}
#
#    def get_instance(*args, **kwargs):
#        if cls not in instances:
#            instances[cls] = cls(*args, **kwargs)
#        return instances[cls]
#
#    get_instance.init = get_instance
#
#    return get_instance

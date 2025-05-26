from utils.singleton_decorator import singleton


@singleton
class GVars:
    def __init__(self):
        self.time = 0
        self.delta_time = 0
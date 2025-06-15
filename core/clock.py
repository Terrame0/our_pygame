from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from utils.debug import debug
import time
from core.event_manager import EventManager
from utils import custom_events


@singleton
class Clock:
    def __init__(self):
        self.delta_time = 0  # -- time since last tick() call
        self.time_snapshot = time.time()  # -- time at last tick() call
        self.start_time = time.time()  # -- time at clock creation
        self.frame_count = 1
        EventManager().subscribe(custom_events.UPDATE,self.tick)

    def tick(self):
        self.delta_time = time.time() - self.time_snapshot
        self.time_snapshot = time.time()
        self.frame_count += 1

    @property
    def avg_fps(self) -> float:
        return 1 / ((self.time_snapshot - self.start_time) / self.frame_count)

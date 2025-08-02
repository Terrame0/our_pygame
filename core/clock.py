from collections import deque
from OpenGL.GL import *
from pygame.locals import *
from utils.singleton_decorator import singleton
from core.event_manager import EventManager
from utils import custom_events
import time
from pyglm import glm


@singleton
class Clock:
    def __init__(self):
        self.delta_time = 0  # -- time since last tick() call
        self.now = time.time()  # -- time at last tick() call
        self.start_time = time.time()  # -- time at clock creation
        self.frame_count = 1

        self.frame_timestamps = deque([self.now])

        EventManager.subscribe(custom_events.UPDATE, self.tick)

    def tick(self):
        current_time = time.time()
        self.delta_time = current_time - self.now
        self.now = current_time
        self.frame_count += 1

        self.frame_timestamps.append(current_time)
        while current_time - self.frame_timestamps[0] > 1.0:
            self.frame_timestamps.popleft()

    @property
    def fps(self):
        return len(self.frame_timestamps)

    @property
    def avg_fps(self):
        return 1 / max((self.now - self.start_time) / self.frame_count,glm.epsilon())

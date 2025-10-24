from OpenGL.GL import *
from utils.gl_constant_map import get_gl_name
from utils.debug import debug
from pyglm import glm
import numpy as np


class Buffer:
    def __init__(self, target, storage_flags=0):
        self.id = glGenBuffers(1)
        self.target = target
        self.storage_flags = (
            storage_flags | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT
        )
        self.sync_objects = []
        # -- information about buffer contents
        self.size = None
        self.nbytes = None
        self.element_type = None
        debug.log(f"constructing a {self}")

    def upload_data(self, data):
        self.size = data.size
        self.nbytes = data.nbytes
        if self.size == 0:
            raise Error("(!) the array cannot be empty")
        if not isinstance(data, np.ndarray):
            raise TypeError("(!) must be a numpy array")
        self.element_type = data.dtype
        with self:
            glBufferStorage(self.target, data.nbytes, data, self.storage_flags)

    def get_data(self):
        if self.element_type is None:
            raise Error("(!) trying to get data from an uninitialized buffer")
        data = np.zeros(self.size, dtype=self.element_type)
        glGetNamedBufferSubData(self.id, 0, self.nbytes, data)
        return data

    def get_address(self):
        with self:
            return glMapBufferRange(self.target, 0, self.nbytes, self.storage_flags)

    def map_to_cstruct(self, cstruct):
        with self:
            return cstruct.from_address(
                glMapBufferRange(self.target, 0, self.nbytes, self.storage_flags)
            )

    def map_to_array(self) -> np.ndarray:
        np_array = None
        with self:
            ptr = glMapBufferRange(self.target, 0, self.nbytes, self.storage_flags)
            np_array = np.frombuffer(
                (ctypes.c_byte * self.nbytes).from_address(ptr),
                dtype=self.element_type,
            )
        return np_array

    # -- TODO FINISH WRITING THIS
    # def wait_for_upload(self):
    #    while self.sync_objects:
    #        sync = self.sync_objects.pop(0)
    #        wait_result = glClientWaitSync(sync, GL_SYNC_FLUSH_COMMANDS_BIT, 1000000000)
    #        if wait_result in [GL_ALREADY_SIGNALED, GL_CONDITION_SATISFIED]:
    #            glDeleteSync(sync)
    #        else:
    #            # Timeout or error, put sync back and try again next frame
    #            self.sync_objects.insert(0, sync)
    #            break

    def __len__(self):
        return self.size

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        glBindBuffer(self.target, self.id)

    def bind_base(self, slot: int, target):
        with self as buffer:
            glBindBufferBase(target, slot, buffer.id)

    def unbind(self):
        glBindBuffer(self.target, 0)

    def __str__(self):
        return f"[{get_gl_name(int(self.target))}] [{self.id}]"

    def delete(self):
        glDeleteBuffers(self.id)

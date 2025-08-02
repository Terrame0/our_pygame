import ctypes
from pyglm import glm
from utils.flatten import flatten
import numpy as np


def create_struct(align=True, **field_defs):

    TYPE_MAP = {
        # -- floats
        glm.float32: (ctypes.c_float * 1, 4),
        glm.vec2: (ctypes.c_float * 2, 8),
        glm.vec3: (ctypes.c_float * 3, 16),
        glm.vec4: (ctypes.c_float * 4, 16),
        # -- matrices
        glm.mat2: (ctypes.c_float * 4, 8),
        glm.mat3: (ctypes.c_float * 12, 16),
        glm.mat4: (ctypes.c_float * 16, 16),
        # -- integers
        glm.int32: (ctypes.c_int32 * 1, 4),
        glm.ivec2: (ctypes.c_int32 * 2, 8),
        glm.ivec3: (ctypes.c_int32 * 3, 16),
        glm.ivec4: (ctypes.c_int32 * 4, 16),
        # -- unsigned integers
        glm.uint32: (ctypes.c_uint32 * 1, 4),
        glm.uvec2: (ctypes.c_uint32 * 2, 8),
        glm.uvec3: (ctypes.c_uint32 * 3, 16),
        glm.uvec4: (ctypes.c_uint32 * 4, 16),
        # -- quaternions
        glm.quat: (ctypes.c_float * 4, 16),
    }

    fields = []
    current_offset = 0
    padding_count = 0
    max_alignment = 1

    for name, field_type in field_defs.items():
        try:
            ctype, alignment = TYPE_MAP[field_type]
        except KeyError:
            raise ValueError(f"(!) unsupported type: {field_type.__name__}")

        if align:
            # -- required padding calculation
            padding_needed = (-current_offset) % alignment
            if padding_needed > 0:
                pad_name = f"pad_{padding_count}"
                fields.append((pad_name, ctypes.c_byte * padding_needed))
                padding_count += 1
                current_offset += padding_needed

        # -- field initialization
        fields.append((name, ctype))
        current_offset += ctypes.sizeof(ctype)
        max_alignment = max(max_alignment, alignment)

    if align:
        # -- final padding (to align the structure in an array)
        struct_padding = (-current_offset) % max_alignment
        if struct_padding > 0:
            pad_name = f"pad_{padding_count}"
            fields.append((pad_name, ctypes.c_byte * struct_padding))

    # -- ctypes struct declaration
    class GLMStruct(ctypes.Structure):
        _fields_ = fields
        _pack_ = 1  # -- to ensure tight packing with manual alignment

        # -- memcopies the underlying object data to an address of an element of a numpy array
        def assign_to_element(self, arr: np.ndarray, *index: list):
            if ctypes.sizeof(self) != arr.dtype.itemsize:
                raise ValueError("(!) size mismatch between structure and array element")
            element_address = arr.ctypes.data + sum(
                [arr.strides[i] * axis for i, axis in enumerate(index)]
            )
            ctypes.memmove(element_address, ctypes.addressof(self), ctypes.sizeof(self))

        def __init__(self, *args, **kwargs):
            super().__init__()
            # -- initialize with values if provided
            for i, (name, field_type) in enumerate(field_defs.items()):
                if i < len(args):
                    # -- flattens the type to a list, unrolls it, converts it to a ctypes array of the mapped type and sets the attribute
                    setattr(self, name, TYPE_MAP[field_type][0](*list(flatten(args[i]))))
                elif name in kwargs:
                    # -- does the same but for kwargs
                    setattr(self, name, TYPE_MAP[field_type][0](*list(flatten(kwargs[name]))))

    GLMStruct.size = ctypes.sizeof(GLMStruct)

    return GLMStruct

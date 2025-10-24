from __future__ import annotations
import ctypes
from pyglm import glm
import numpy as np


def create_struct(do_align=True, **FIELD_GLM_TYPES):

    # -- ALL MUST BE GLM TYPES!!!
    TYPE_MAP = {
        # -- floats
        glm.vec1: (ctypes.c_float * 1, 4),
        glm.vec2: (ctypes.c_float * 2, 8),
        glm.vec3: (ctypes.c_float * 3, 16),
        glm.vec4: (ctypes.c_float * 4, 16),
        # -- matrices
        glm.mat2: (ctypes.c_float * 4, 8),
        glm.mat3: (ctypes.c_float * 12, 16),
        glm.mat4: (ctypes.c_float * 16, 16),
        # -- integers
        glm.ivec1: (ctypes.c_int32 * 1, 4),
        glm.ivec2: (ctypes.c_int32 * 2, 8),
        glm.ivec3: (ctypes.c_int32 * 3, 16),
        glm.ivec4: (ctypes.c_int32 * 4, 16),
        # -- unsigned integers
        glm.uvec1: (ctypes.c_uint32 * 1, 4),
        glm.uvec2: (ctypes.c_uint32 * 2, 8),
        glm.uvec3: (ctypes.c_uint32 * 3, 16),
        glm.uvec4: (ctypes.c_uint32 * 4, 16),
        # -- quaternions
        glm.quat: (ctypes.c_float * 4, 16),
    }

    # -- sanity check (all are, indeed, glm types)
    for entry in TYPE_MAP.keys():
        try:
            glm.value_ptr(entry())
        except:
            raise Exception(f"(!) {entry} is not a glm type!")

    FIELD_CTYPES = {}  # -- {name: ctypes type}
    FIELD_OFFSETS = {}  # -- {name: offset}

    current_offset = 0
    padding_count = 0
    max_alignment = 1

    for name, glm_field_type in FIELD_GLM_TYPES.items():
        try:
            ctype, alignment = TYPE_MAP[glm_field_type]
        except KeyError:
            raise ValueError(f"(!) unsupported type: {glm_field_type.__name__}")

        if do_align:
            # -- required padding calculation
            padding_needed = (-current_offset) % alignment
            if padding_needed > 0:
                pad_name = f"pad_{padding_count}"
                FIELD_CTYPES[pad_name] = ctypes.c_byte * padding_needed
                padding_count += 1
                current_offset += padding_needed

        # -- field initialization
        FIELD_CTYPES[name] = ctype
        FIELD_OFFSETS[name] = current_offset
        current_offset += ctypes.sizeof(ctype)
        max_alignment = max(max_alignment, alignment)

    if do_align:
        # -- final padding (to align the structure in an array)
        struct_padding = (-current_offset) % max_alignment
        if struct_padding > 0:
            pad_name = f"pad_{padding_count}"
            FIELD_CTYPES[pad_name] = ctypes.c_byte * struct_padding

    # -- ctypes struct declaration
    class GLMStruct(ctypes.Structure):
        # -- leaving only ctypes
        _fields_ = list(FIELD_CTYPES.items())
        _pack_ = 1  # -- to ensure tight packing with manual alignment

        # -- memcopies the underlying object data to an address of an element of a numpy array
        def assign_to_element(self, arr: np.ndarray, *index: list):
            if ctypes.sizeof(self) != arr.dtype.itemsize:
                raise ValueError("(!) size mismatch between structure and array element")
            element_address = arr.ctypes.data + sum(
                [arr.strides[i] * axis for i, axis in enumerate(index)]
            )
            ctypes.memmove(element_address, ctypes.addressof(self), ctypes.sizeof(self))

        def __setattr__(self, name, value):
            if name in FIELD_GLM_TYPES:  # -- checks if a name is a field
                glm_type = FIELD_GLM_TYPES[name]
                if type(value) is not glm_type:  # -- if types do not match
                    try:
                        # -- tries to cast value into the field's type
                        value = glm_type(value)
                    except:
                        # -- if fails to do so, throws an error
                        raise TypeError(f"(!) can't convert {type(value)} into {glm_type}")
                # -- if all went well, memcopies data of the glm type into the structure with the attribute's offset
                ctypes.memmove(
                    ctypes.addressof(super().__getattribute__(name)),
                    glm.value_ptr(value),
                    glm.sizeof(value),
                )
            else:
                super().__setattr__(name, value)

        # -- the object that is returned contains COPIED data
        def __getattribute__(self, name):
            if name in FIELD_GLM_TYPES:  # -- checks if a name is a field
                glm_type = FIELD_GLM_TYPES[name]
                glm_instance = None
                field_address = ctypes.addressof(super().__getattribute__(name))
                field_ptr = ctypes.cast(
                    field_address,
                    ctypes.POINTER(ctypes.c_float),
                )
                try:  # -- if a make_* function exists, calls it
                    glm_instance = getattr(glm, f"make_{glm_type.__name__}")(field_ptr)
                except:  # -- if not, dereferences the pointer and returns a value
                    glm_instance = field_ptr.contents.value
                return glm_instance
            else:
                return super().__getattribute__(name)

        @classmethod
        def from_address(cls, address) -> GLMStruct:
            struct_ptr = ctypes.POINTER(cls)
            ptr = ctypes.cast(
                address,
                struct_ptr,
            )
            instance = ptr.contents
            # -- avoids the __getattribute__ call
            cls.__init__(instance)
            return instance

        def __init__(self, *args, **kwargs):
            super().__init__()
            for i, (name, glm_type) in enumerate(FIELD_GLM_TYPES.items()):
                # -- initializes with values if provided
                if i < len(args):
                    setattr(self, name, args[i])
                elif name in kwargs:
                    setattr(self, name, kwargs[name])

    return GLMStruct

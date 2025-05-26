import OpenGL.GL as gl
import sys
from utils.debug import debug

def build_gl_constant_map():
    debug.log("caching gl constant names")
    mapping = {}
    for name, value in vars(gl).items():
        if name.startswith("GL_") and isinstance(value, int):
            mapping[value] = name
    return mapping

gl_constant_map = build_gl_constant_map()

def get_gl_name(value):
    return gl_constant_map.get(int(value), f"UNKNOWN_GL_CONSTANT({value})")
import ctypes
from OpenGL.GL import GL_ARRAY_BUFFER
from pyglm import glm
import numpy as np
from graphics.resources.ctypes_struct import create_struct
from graphics.resources.buffer import Buffer
from typing import List
from pathlib import Path


class Mesh:
    # -- represents vertex gpu memory layout
    vertex_dtype = create_struct(
        position=glm.vec3,
        texcoord=glm.vec2,
        normal=glm.vec3,
        do_align=False,
    )

    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

    @classmethod
    def load_from_file(cls, path: Path):

        # -- getting vertex attributes from a file
        positions, normals, texcoords, faces = cls.parse_obj(path)

        vertex_cache = {}  # -- caches vertex data so that

        # -- filling indices and caching vertex data by iterating over face vertices
        indices = np.zeros(len(faces) * 3, dtype=ctypes.c_uint32)
        vertex_counter = 0
        for i, vtx_info in enumerate([vtx_info for face in faces for vtx_info in face]):
            v_idx = vtx_info[0] - 1
            vt_idx = vtx_info[1] - 1
            vn_idx = vtx_info[2] - 1

            key = (v_idx, vt_idx, vn_idx)
            if key not in vertex_cache:
                vertex_cache[key] = vertex_counter
                vertex_counter += 1
            indices[i] = vertex_cache[key]

        # -- filling vertex array with values from the vertex cache
        interleaved_vertices = np.zeros(vertex_counter, dtype=cls.vertex_dtype)
        for i, (key, _) in enumerate(vertex_cache.items()):
            interleaved_vertices[i]["position"] = positions[key[0]]
            interleaved_vertices[i]["texcoord"] = texcoords[key[1]]
            interleaved_vertices[i]["normal"] = normals[key[2]]
        instance = cls(interleaved_vertices, indices)
        return instance

    @staticmethod
    def parse_obj(path:Path):

        # -- using lists for faster addition
        positions: List[glm.vec3] = []
        normals: List[glm.vec3] = []
        texcoords: List[glm.vec2] = []
        faces: List[List[glm.uvec3]] = []

        with open(str(path), "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                data = line.split()
                if data[0] == "v":
                    positions.append(glm.vec3([float(x) for x in data[1:]]))
                elif data[0] == "vn":
                    normals.append(glm.vec3([float(x) for x in data[1:]]))
                elif data[0] == "vt":
                    texcoords.append(glm.vec2([float(x) for x in data[1:]]))
                elif data[0] == "f":
                    face_data = []
                    for vertex_data in data[1:]:
                        parts = vertex_data.split("/")
                        v = int(parts[0]) if parts[0] else None
                        t = int(parts[1]) if parts[1] else None
                        n = int(parts[2]) if parts[2] else None
                        face_data.append(glm.uvec3(v, t, n))
                    faces.append(face_data)
        return positions, normals, texcoords, faces

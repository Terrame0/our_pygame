from utils.singleton_decorator import singleton
from pathlib import Path
from typing import Dict
from utils.path_resolver import resolve_path
from graphics.resources.mesh import Mesh
import numpy as np
from OpenGL.GL import *
from graphics.resources.buffer import Buffer


@singleton
class MeshLoader:
    def __init__(self):
        self.joint_vertex_buffer = np.array([], dtype=Mesh.vertex_cstruct)
        self.joint_index_buffer = np.array([], dtype=ctypes.c_uint32)

        self.mesh_data: Dict[str, Dict[str, int]] = {}
        self.joint_vao = None

        self.load_meshes()
        self.init_joint_vao()

    def __getitem__(self, name: str) -> Dict[str, int]:
        return self.mesh_data[name]

    def get_mesh_data(self, name: str) -> Dict[str, int]:
        return self.mesh_data[name]

    def load_meshes(self) -> Dict[str, Dict[str, int]]:
        mesh_paths = list(Path(resolve_path("assets/")).glob("**/*.obj"))
        meshes = [Mesh.load_from_file(path=str(s)) for s in mesh_paths]
        index_offset = 0
        vertex_offset = 0
        for mesh, path in zip(meshes, mesh_paths):
            self.mesh_data[path.name] = {
                "size": len(mesh.indices),
                "index_offset": index_offset,
                "vertex_offset": vertex_offset,
            }
            index_offset += len(mesh.indices)
            vertex_offset += len(mesh.vertices)
        self.joint_vertex_buffer = np.concatenate([mesh.vertices for mesh in meshes])
        self.joint_index_buffer = np.concatenate([mesh.indices for mesh in meshes])
        return self.mesh_data

    def init_joint_vao(self):
        # -- vertex array object
        self.joint_vao = glGenVertexArrays(1)
        glBindVertexArray(self.joint_vao)

        # -- vertex buffer
        vbo = Buffer(GL_ARRAY_BUFFER)
        vbo.upload_data(self.joint_vertex_buffer)

        # -- element buffer
        ebo = Buffer(GL_ELEMENT_ARRAY_BUFFER)
        ebo.upload_data(self.joint_index_buffer)

        # -- vertex attributes
        with vbo, ebo:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, None)
            glEnableVertexAttribArray(0)

            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)

            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(5 * 4))
            glEnableVertexAttribArray(2)
            glBindVertexArray(0)
from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from utils.path_resolver import resolve_path
from utils.debug import debug


class Mesh(Module):
    requires = [Transform]

    def __init_module__(self, obj_path: str = ""):
        vertices, normals, texcoords, faces = self.parse_obj(obj_path)
        self.max_vert_radius = 0
        vertex_cache = {}
        interleaved_vertices = []
        indices = []
        for face in faces:
            for vtx_info in face:
                v_idx = vtx_info[0] - 1
                vt_idx = vtx_info[1] - 1
                vn_idx = vtx_info[2] - 1

                key = (v_idx, vt_idx, vn_idx)
                if key not in vertex_cache:
                    vertex_cache[key] = len(interleaved_vertices) // 8
                    v = vertices[v_idx]
                    self.max_vert_radius = max(
                        self.max_vert_radius,
                        glm.distance(glm.vec3(0), glm.vec3(*v)),
                    )
                    vt = texcoords[vt_idx]
                    vn = normals[vn_idx]
                    interleaved_vertices.extend(v + vt + vn)

                indices.append(vertex_cache[key])
        self.vertex_buffer = glm.array.from_numbers(glm.float32, *interleaved_vertices)
        self.index_buffer = glm.array.from_numbers(glm.int32, *indices)
    
    @property
    def bounding_sphere_radius(self):
        return self.max_vert_radius * max(*self.parent_obj.transform.scale) + 0.01

    def parse_obj(self, filepath):
        vertices = []
        normals = []
        texcoords = []
        faces = []

        with open(resolve_path(filepath), "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                data = line.split()
                if data[0] == "v":
                    vertices.append([float(x) for x in data[1:]])
                elif data[0] == "vn":
                    normals.append([float(x) for x in data[1:]])
                elif data[0] == "vt":
                    texcoords.append([float(x) for x in data[1:]])
                elif data[0] == "f":
                    face_data = []
                    for vertex_data in data[1:]:
                        parts = vertex_data.split("/")
                        v = int(parts[0]) if parts[0] else None
                        t = int(parts[1]) if parts[1] else None
                        n = int(parts[2]) if parts[2] else None
                        face_data.append([v, t, n])
                    faces.append(face_data)
        return vertices, normals, texcoords, faces

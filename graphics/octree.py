from __future__ import annotations
from scene.gizmos.bounding_box import AABB
from pyglm import glm
from itertools import product
from graphics.resources.ctypes_struct import create_struct

# tree_node_cstruct = create_struct(
#     child_000=glm.uvec1,
#     child_001=glm.uvec1,
#     child_010=glm.uvec1,
#     child_011=glm.uvec1,
#     child_100=glm.uvec1,
#     child_101=glm.uvec1,
#     child_110=glm.uvec1,
#     child_111=glm.uvec1,
# )


class OctreeNode:
    def __init__(self, p1, p2, depth=0):
        self.aabb = AABB(p1, p2)
        self.points = []
        self.children = []
        self.capacity = 1
        self.depth = depth
        self.is_subdivided = False

    def subdivide(self):
        midpoint: glm.vec3 = (self.aabb.p1 + self.aabb.p2) / 2
        for axis_product in product(range(2), repeat=3):
            self.children.append(
                OctreeNode(
                    glm.vec3(
                        [
                            self.aabb.p1[axis] if axis_product[axis] == 0 else midpoint[axis]
                            for axis in range(3)
                        ]
                    ),
                    glm.vec3(
                        [
                            midpoint[axis] if axis_product[axis] == 0 else self.aabb.p2[axis]
                            for axis in range(3)
                        ]
                    ),
                    self.depth + 1,
                )
            )

    def insert(self, point) -> bool:
        if not self.aabb.contains(point):
            return False  # -- failed to insert
        if not self.is_subdivided and len(self.points) < self.capacity:
            self.points.append(point)
            self.aabb.object.renderer.is_transparent = True
            self.aabb.object.renderer.mesh = "unit_cube.obj"
            self.aabb.object.renderer.texture = "error.png"
            return True  # -- inserted successfuly
        else:
            points_to_distribute = [point]
            if not self.is_subdivided:
                self.subdivide()
                points_to_distribute += self.points
                self.points = []
                self.is_subdivided = True
                self.aabb.object.renderer.is_visible = False

            for p in points_to_distribute:
                for child in self.children:
                    if child.insert(p):
                        break  # -- child insertion successful, breaking out of the loop
            return True
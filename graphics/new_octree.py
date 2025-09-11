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


class NewOctreeNode:
    def __init__(self, p1, p2, depth=0):
        self.aabb = AABB(p1, p2)
        self.boxes = []
        self.children = []
        self.depth = depth
        self.is_subdivided = False

    def subdivide(self):
        midpoint: glm.vec3 = (self.aabb.p1 + self.aabb.p2) / 2
        for axis_product in product(range(2), repeat=3):
            self.children.append(
                NewOctreeNode(
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

    # def fits_into_children(self, box: AABB):
    #    midpoint: glm.vec3 = (self.aabb.p1 + self.aabb.p2) / 2
    #    for axis_product in product(range(2), repeat=3):
    #        test_aabb = AABB(
    #            glm.vec3(
    #                [
    #                    self.aabb.p1[axis] if axis_product[axis] == 0 else midpoint[axis]
    #                    for axis in range(3)
    #                ]
    #            ),
    #            glm.vec3(
    #                [
    #                    midpoint[axis] if axis_product[axis] == 0 else self.aabb.p2[axis]
    #                    for axis in range(3)
    #                ]
    #            ),
    #        )
    #        if test_aabb.contains_aabb(box):
    #            return True
    #    return False

    def insert(self, box: AABB) -> bool:
        if not self.aabb.contains(box):
            return False  # -- insertion FAILS if does not fit

        # -- if the box fits into the node aabb,
        # -- tries to fit into any of the children
        if not self.is_subdivided:
            self.subdivide()
            self.boxes = []
            self.is_subdivided = True
            self.aabb.object.renderer.is_visible = False
        insert_successful = False
        for child in self.children:
            if child.insert(box):
                insert_successful = True
        if insert_successful:
            return True
        self.boxes.append(box)
        self.aabb.object.renderer.is_transparent = True
        self.aabb.object.renderer.mesh = "unit_cube.obj"
        self.aabb.object.renderer.texture = "error.png"
        return True  # -- inserted successfuly

        # else:
        #    boxes_to_distribute = [box]
        #    if not self.is_subdivided:
        #        self.subdivide()
        #        boxes_to_distribute += self.boxes
        #        self.boxes = []
        #        self.is_subdivided = True
        #        self.aabb.object.renderer.is_visible = False
        #
        #    for p in boxes_to_distribute:
        #        for child in self.children:
        #            if child.insert(p):
        #                break  # -- child insertion successful, breaking out of the loop
        #    return True
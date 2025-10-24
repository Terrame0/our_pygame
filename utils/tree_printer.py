from __future__ import annotations
import numpy as np
from scene.scene_object import SceneObject
from scene.modules.renderer import Renderer
from scene.modules.transform import Transform


class TreeVisualizer:
    gizmos: SceneObject = []

    @classmethod
    def draw(cls, node):
        for obj in cls.gizmos:
            obj.destroy()
        cls.gizmos.clear()
        cls.recurse(node)

    @classmethod
    def recurse(
        cls,
        node,
    ):
        if not node is None:
            cls.gizmos.append(
                SceneObject(
                    modules=[
                        Transform(
                            scale=node.aabb.extent,
                            position=node.aabb.min_p,
                        ),
                        Renderer(
                            mesh="unit_cube.obj",
                            texture="blue.png" if node.is_leaf else "black.png",
                            is_transparent=True,
                        ),
                    ]
                )
            )
            if not node.is_leaf:
                cls.recurse(node.left)
                cls.recurse(node.right)


class TreePrinter:

    str_len: list = [1, 3, 5]
    layer_h = 4

    @classmethod
    def print(cls, node):

        max_depth = cls.probe_depth(node, 0)
        width = max(cls.str_len) * (2**max_depth) + (2**max_depth) - 1
        height = (max_depth + 1) * cls.layer_h + 1
        max_spacing = width // 2
        charmap = np.zeros((height, width), dtype=str)
        cls.recurse(node, charmap, max_spacing, 0, max_spacing, True)

        for row in charmap[0 : charmap.shape[0] - 1]:
            print(*[char if char != "" else " " for char in row], sep="")

    @classmethod
    def probe_depth(
        cls,
        node,
        depth,
    ):
        max_depth = depth
        if not node is None and not node.is_leaf:
            max_depth = max(
                cls.probe_depth(node.left, depth + 1),
                cls.probe_depth(node.right, depth + 1),
            )
        return max(depth, max_depth)

    @classmethod
    def recurse(
        cls,
        node,
        charmap,
        max_spacing,
        depth,
        position,
        even,
    ):

        base_row_id = depth * cls.layer_h
        offset = max_spacing // (2 ** (depth + 1))

        if not even:
            charmap[
                base_row_id - 1, position - (max_spacing // (2**depth)) * 2 - 1 : position
            ] = "─"
            charmap[base_row_id - 1, position - max_spacing // (2**depth) - 1] = "┴"

        charmap[
            base_row_id - 1, position - cls.str_len[0] // 2 : position + cls.str_len[0] // 2 + 1
        ] = list(f"{'╭' if even else '╮'}")

        charmap[
            base_row_id, position - cls.str_len[0] // 2 : position + cls.str_len[0] // 2 + 1
        ] = list(f"{node.name}")

        charmap[
            base_row_id + 1, position - cls.str_len[1] // 2 : position + cls.str_len[1] // 2 + 1
        ] = list(f"({node.parent.name if node.parent is not None else '#'})")

        charmap[
            base_row_id + 2, position - cls.str_len[2] // 2 : position + cls.str_len[2] // 2 + 1
        ] = list(f"{str(node.aabb.area).rjust(5,' ')}"[0:5])

        if not node is None and not node.is_leaf:
            cls.recurse(
                node.left,
                charmap,
                max_spacing,
                depth + 1,
                position - offset - 1,
                True,
            )
            cls.recurse(
                node.right,
                charmap,
                max_spacing,
                depth + 1,
                position + offset + 1,
                False,
            )
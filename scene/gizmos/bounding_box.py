from __future__ import annotations
from pyglm import glm
import numpy as np
from itertools import combinations
from typing import List
import sys


class RelaxedAABB:
    def __init__(self, inner_aabb: AABB):
        self.inner_aabb = inner_aabb
        self.outer_aabb = inner_aabb.grow(0.1).clone()

    def needs_refit(self):
        return not self.outer_aabb.contains(self.inner_aabb)


class AABB:
    def __init__(self, p1=glm.vec3(0), p2=glm.vec3(0)):
        self.p1 = p1
        self.p2 = p2

    @classmethod
    def fit(cls, *points: List[glm.vec3]):
        min_p = glm.vec3(sys.float_info.max)
        max_p = glm.vec3(-sys.float_info.max)
        for point in points:
            min_p = glm.min(min_p, point)
            max_p = glm.max(max_p, point)
        return cls(min_p, max_p)

    def contains(self, other: AABB) -> bool:
        return np.all(other.min_p >= self.min_p) and np.all(other.max_p <= self.max_p)

    def intersects(self, other: AABB) -> bool:
        return not (np.any(other.max_p < self.min_p) or np.any(other.min_p > self.max_p))

    @staticmethod
    def union(b1: AABB, b2: AABB) -> AABB:
        return AABB(
            glm.min(b1.min_p, b2.min_p),
            glm.max(b1.max_p, b2.max_p),
        )

    def clone(self) -> AABB:
        return AABB(self.p1, self.p2)

    def grow(self, distance: float) -> AABB:
        self.p1 = self.min_p - distance
        self.p2 = self.max_p + distance
        return self

    @property
    def extent(self) -> glm.vec3:
        return glm.abs(self.p1 - self.p2)

    @property
    def center(self) -> glm.vec3:
        return (self.p1 + self.p2) / 2

    @property
    def area(self) -> float:
        return np.sum([np.prod(side) * 2 for side in combinations(self.extent, 2)])

    @property
    def min_p(self) -> glm.vec3:
        return glm.min(self.p1, self.p2)

    @property
    def max_p(self) -> glm.vec3:
        return glm.max(self.p1, self.p2)

    def __str__(self):
        return f"AABB[{self.p1}, {self.p2}]"

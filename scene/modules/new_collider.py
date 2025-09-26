from pyglm import glm
from scene.modules.module_base import Module
from scene.modules.transform import Transform
from scene.modules.renderer import Renderer
from scene.modules.physics_body import PhysicsBody
from OpenGL.GL import *
from pyglm import glm
from typing import Tuple
from scene.gizmos.bounding_box import AABB
from scene.scene import Scene
from scene.scene_object import SceneObject
from core.event_system.user_events import UserEvents
from graphics.bvh import BVHNode
from utils.tree_printer import TreeVisualizer


class NewCollider(Module):
    requires = [Transform, Renderer]
    offset = 0.2

    def __init_module__(self):
        self.mesh_aabb = self.parent_obj.renderer.mesh.aabb
        self.outer_aabb = AABB(self.mesh_aabb.p1, self.mesh_aabb.p2)
        self.relaxed_aabb = AABB(
            self.mesh_aabb.min_p - self.offset,
            self.mesh_aabb.max_p + self.offset,
        )
        self.node_handle = BVHNode.as_leaf(self.relaxed_aabb)

        Scene.bvh.insert(self.node_handle)

        self.init_visualization()
        self.subscribe_to_event(UserEvents["update"], self.update_visualization)

        self.recalculate_outer_aabb()
        self.subscribe_to_event(
            UserEvents["transform_update"],
            self.recalculate_outer_aabb,
            progenitor=self.parent_obj,
        )
        self.subscribe_to_event(
            UserEvents["transform_update"],
            self.recalculate_relaxed_aabb,
            progenitor=self.parent_obj,
        )

    def recalculate_relaxed_aabb(self):
        if not self.relaxed_aabb.contains(self.outer_aabb):
            # TreeVisualizer.draw(Scene.bvh.root)
            self.relaxed_aabb.p1 = self.outer_aabb.min_p - self.offset
            self.relaxed_aabb.p2 = self.outer_aabb.max_p + self.offset
            Scene.bvh.reinsert(self.node_handle)

    def recalculate_outer_aabb(self):
        half_extents = self.mesh_aabb.extent / 2
        R = self.parent_obj.transform.R
        vx = glm.abs(R * glm.vec3(half_extents.x, 0, 0))
        vy = glm.abs(R * glm.vec3(0, half_extents.y, 0))
        vz = glm.abs(R * glm.vec3(0, 0, half_extents.z))
        new_half_extents = glm.vec3(
            vx.x + vy.x + vz.x,
            vx.y + vy.y + vz.y,
            vx.z + vy.z + vz.z,
        )
        new_center = self.parent_obj.transform.model_matrix * self.mesh_aabb.center

        self.outer_aabb.p1 = new_center - new_half_extents
        self.outer_aabb.p2 = new_center + new_half_extents

    def init_visualization(self):
        self.outer_aabb_vis = SceneObject(
            name=f"{self.parent_obj.name}_aabb",
            modules=[
                Transform,
                Renderer(mesh="unit_cube.obj", texture="error.png", is_transparent=True),
            ],
        )
        self.relaxed_aabb_vis = SceneObject(
            name=f"{self.parent_obj.name}_aabb",
            modules=[
                Transform,
                Renderer(mesh="unit_cube.obj", texture="error.png", is_transparent=True),
            ],
        )
        self.inner_aabb_vis = SceneObject(
            name=f"{self.parent_obj.name}_aabb",
            modules=[
                Transform,
                Renderer(mesh="unit_cube.obj", texture="blue.png", is_transparent=True),
            ],
        )

    def update_visualization(self):
        self.outer_aabb_vis.transform.position = self.outer_aabb.min_p
        self.outer_aabb_vis.transform.scale = self.outer_aabb.extent

        self.relaxed_aabb_vis.transform.position = self.relaxed_aabb.min_p
        self.relaxed_aabb_vis.transform.scale = self.relaxed_aabb.extent

        self.inner_aabb_vis.transform.quaternion = self.parent_obj.transform.quaternion
        self.inner_aabb_vis.transform.scale = (
            self.parent_obj.transform.scale * self.mesh_aabb.extent
        )
        self.inner_aabb_vis.transform.position = (
            self.parent_obj.transform.model_matrix * self.mesh_aabb.p1
        )
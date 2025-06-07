
from graphics.graphics_backend import GraphicsBackend
from graphics.texture import Texture
from utils import custom_events
from core.event_manager import EventManager
from scene.modules.transform import Transform
from scene.modules.mesh import Mesh
from scene.scene_object import SceneObject
from scene.modules.camera import Camera
from scene.modules.renderer import Renderer
import pygame
from pyglm import glm
from scene.scene import Scene
from utils.debug import debug


class Projectile:
    def __init__(self, parent):

        # -- state
        self.destroyed = False
        self.creation_time = GraphicsBackend().clock.time_snapshot

        # -- who this projectile belongs to
        self.parent = parent

        self.obj = SceneObject(name="projectile")
        self.obj.add_module(Transform)
        self.obj.add_module(Mesh, obj_path="assets/plane.obj")
        self.obj.add_module(Renderer, is_transparent=True)
        self.obj.renderer.texture = Texture(0, "assets/plasma.png")
        self.obj.transform.scale = glm.vec3(0.1)
        self.obj.transform.quaternion = self.parent.obj.transform.quaternion

        # -- constants
        self.collision_radius = self.obj.mesh.bounding_sphere_radius

        # -- setting initial transform values
        self.velocity = (
            self.parent.velocity.xyz
            + self.parent.obj.transform.R * glm.vec3(0, 0, -1) * 10
        )
        self.obj.transform.position = (
            self.parent.obj.transform.position.xyz
            + self.parent.obj.transform.R * glm.vec3(0, -0.1, -0.3)
        )

        # -- event manager subscriptions
        EventManager().subscribe(custom_events.UPDATE, self.update)
        EventManager().subscribe(custom_events.UPDATE, self.check_collisions)

    # -- TODO move this to a rigidbody module
    def check_collisions(self):
        for obj in Scene().object_list:
            if (
                hasattr(obj, "collider")
                and glm.distance(obj.transform.position, self.obj.transform.position)
                <= obj.mesh.bounding_sphere_radius + self.collision_radius
            ):
                distance_test: glm.vec4 = obj.collider.dist_to_point(
                    self.obj.transform.position
                )
                if (
                    obj.collider.dist_to_point(self.obj.transform.position).x
                    < self.collision_radius
                ):
                    self.obj.transform.position += (
                        distance_test.yzw
                        / glm.length(distance_test.yzw)
                        * (self.collision_radius - distance_test.x)
                    )
                    self.velocity = glm.reflect(
                        self.velocity, distance_test.yzw / glm.length(distance_test.yzw)
                    )

    def update(self):
        if GraphicsBackend().clock.time_snapshot - self.creation_time > 20:
            self.destroy()
        clock = GraphicsBackend().clock
        self.obj.transform.quaternion = self.parent.obj.transform.quaternion
        self.obj.transform.position += self.velocity * clock.delta_time

    def destroy(self):
        self.destroyed = True
        EventManager().unsubscribe(custom_events.UPDATE, self.update)
        EventManager().unsubscribe(custom_events.UPDATE, self.check_collisions)
        if self in self.parent.projectile_list:
            self.parent.projectile_list.remove(self)
        Scene().object_list.remove(self.obj)
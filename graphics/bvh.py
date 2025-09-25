from __future__ import annotations
from scene.gizmos.bounding_box import AABB
from pyglm import glm
from itertools import product
from graphics.resources.ctypes_struct import create_struct
from utils.debug import debug
from collections import defaultdict
import numpy as np
import heapq


class BVHNode:
    capital_letter = 65
    lowercase_letter = 97

    def __lt__(self, other):
        return self.aabb.area < other.aabb.area

    @classmethod
    def as_branch(cls, left: BVHNode, right: BVHNode):
        instance = cls()

        instance.name = chr(cls.lowercase_letter)
        cls.lowercase_letter += 1

        left.parent = instance
        right.parent = instance
        instance.left = left
        instance.right = right

        instance.aabb = AABB.union(left.aabb, right.aabb)

        return instance

    @classmethod
    def as_leaf(cls, aabb: AABB, parent: BVHNode = None):
        instance = cls()

        instance.name = chr(cls.capital_letter)
        cls.capital_letter += 1

        instance.parent = parent

        instance.aabb = aabb

        return instance

    @property
    def is_leaf(self):
        return not (hasattr(self, "left") or hasattr(self, "right"))


class BVH:

    def __init__(self):
        self.root = None

    def insert(self, leaf: BVHNode) -> None:

        print(leaf.aabb)

        # -- if the tree is empty
        if self.root is None:
            self.root = leaf
            return

        # -- best candidate to group the leaf with
        sibling = self.find_sibling(leaf)

        # -- remembering the old parent
        # -- (has to be done BEFORE the next step as the parent
        # -- of the sibling will be changed by the "as_branch" constructor)
        old_parent = sibling.parent

        # -- creating a new parent in place of the sibling
        # -- so that the leaf and its sibling are its children
        new_parent = BVHNode.as_branch(sibling, leaf)

        # -- if sibling is not the root
        if old_parent is not None:
            # -- swapping the sibling with the new parent
            if old_parent.left is sibling:
                old_parent.left = new_parent
            else:
                old_parent.right = new_parent
            # -- grafting the new parent back onto the tree
            new_parent.parent = old_parent

        # -- if sibling is the root
        else:
            # -- making new parent the new root
            self.root = new_parent
            new_parent.parent = None

        # -- refits aabbs from leaf-up recursively
        # -- (makes sure that parent aabbs encompass their children)
        self.refit(leaf)

        # -- performs transformations that reduce the cost of the tree (SAH)
        self.balance(leaf)

    def remove(self, leaf: BVHNode):
        cur = leaf
        while cur.parent is not None:
            cur = cur.parent
        if cur is not self.root:
            raise ValueError("(!) node to remove is not in the tree")

        parent = leaf.parent

        # -- node is root
        if parent is None:
            self.root = None
            return

        grand_parent = parent.parent
        sibling = parent.left if parent.right == leaf else parent.right

        # -- node has grandparent
        if grand_parent is not None:
            sibling.parent = grand_parent
            if grand_parent.left == parent:
                grand_parent.left = sibling
            else:
                grand_parent.right = sibling

            ancestor = grand_parent
            while ancestor is not None:
                # -- recalculate AABB from children
                ancestor.aabb = AABB.union(ancestor.left.aabb, ancestor.right.aabb)

                # -- balance the tree at this level
                self.balance(ancestor)

                ancestor = ancestor.parent
        else:
            # -- parent was the root, so sibling becomes the new root
            self.root = sibling
            sibling.parent = None

    def reinsert(self, leaf: BVHNode):
        self.remove(leaf)
        self.insert(leaf)

    def find_sibling(self, leaf: BVHNode):
        # -- if the tree only has one node (the root)
        if self.root.is_leaf:
            return self.root

        best_sibling = self.root
        best_cost = AABB.union(self.root.aabb, leaf.aabb).area

        # -- using priority queue for best-first search
        # -- we'll store tuples of (priority, counter, inherited_cost, node)
        queue = []
        counter = 0
        heapq.heappush(queue, (0, counter, 0, self.root))
        counter += 1

        while queue:
            # -- get the node with the lowest priority
            _, _, inherited_cost, current = heapq.heappop(queue)

            # -- calculate the direct cost of making this node a sibling
            combined_aabb = AABB.union(current.aabb, leaf.aabb)
            direct_cost = combined_aabb.area
            total_cost = direct_cost + inherited_cost

            # -- update best candidate if this is better
            if total_cost < best_cost:
                best_cost = total_cost
                best_sibling = current

            # -- if current is a leaf, we can't explore further
            if current.is_leaf:
                continue

            # -- calculate the inherited cost for children
            # -- this is the cost of expanding the current node's AABB to include the new leaf
            child_inherited_cost = inherited_cost + direct_cost - current.aabb.area

            # -- calculate lower bound for children
            child_lower_bound = leaf.aabb.area + child_inherited_cost

            # -- only explore children if they might yield a better solution
            if child_lower_bound < best_cost:
                # -- push left child with unique counter
                heapq.heappush(
                    queue, (child_lower_bound, counter, child_inherited_cost, current.left)
                )
                counter += 1

                # -- push right child with unique counter
                heapq.heappush(
                    queue, (child_lower_bound, counter, child_inherited_cost, current.right)
                )
                counter += 1

        return best_sibling

    def refit(self, node: BVHNode):
        while node is not None:
            if not node.is_leaf:
                left_aabb = node.left.aabb
                right_aabb = node.right.aabb
                node.aabb = AABB.union(left_aabb, right_aabb)
            node = node.parent

    def balance(self, node: BVHNode):
        # -- running the loop bottom-up
        # -- until we get out the root
        while node is not None:
            # -- skipping to the next iteration
            # -- if the node is a leaf
            if node.is_leaf:
                node = node.parent
                continue

            costs = np.full(4, np.inf)  # -- costs to apply tree transformations

            left = node.left
            right = node.right

            # -- calculating costs
            if not node.left.is_leaf:
                left_area = left.aabb.area
                costs[0] = AABB.union(left.left.aabb, right.aabb).area - left_area
                costs[1] = AABB.union(left.right.aabb, right.aabb).area - left_area
            if not node.right.is_leaf:
                right_area = right.aabb.area
                costs[2] = AABB.union(right.left.aabb, left.aabb).area - right_area
                costs[3] = AABB.union(right.right.aabb, left.aabb).area - right_area

            # -- choosing the best transformation
            best_id = best_id = np.argmin(costs)

            # -- skipping to the next iteration if
            # -- the best transformation results in
            # -- no decrease in surface area
            if costs[best_id] >= 0:
                node = node.parent
                continue

            if best_id == 0:
                self.swap_nodes(right, left.right)
                left.aabb = AABB.union(left.left.aabb, left.right.aabb)
            elif best_id == 1:
                self.swap_nodes(right, left.left)
                left.aabb = AABB.union(left.left.aabb, left.right.aabb)
            elif best_id == 2:
                self.swap_nodes(left, right.right)
                right.aabb = AABB.union(right.left.aabb, right.right.aabb)
            elif best_id == 3:
                self.swap_nodes(left, right.left)
                right.aabb = AABB.union(right.left.aabb, right.right.aabb)

            node = node.parent

    def swap_nodes(self, this: BVHNode, other: BVHNode):
        if this.parent is not None and other.parent is not None:
            # -- remembering child positions and parents
            # -- because they will get changed
            this_pos = "l" if this.parent.left is this else "r"
            other_pos = "l" if other.parent.left is other else "r"
            this_parent = this.parent
            other_parent = other.parent

            if this_pos == "l":
                this_parent.left = other
            else:
                this_parent.right = other
            other.parent = this_parent

            if other_pos == "l":
                other_parent.left = this
            else:
                other_parent.right = this
            this.parent = other_parent

        else:
            print("cant swap with root")
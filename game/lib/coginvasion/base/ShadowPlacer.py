########################################
# Filename: ShadowPlacer.py
# Created by: blach (11Aug14)
########################################

from panda3d.core import CollisionRay, CollisionNode, BitMask32
from panda3d.core import CollisionHandlerFloor
from lib.coginvasion.globals import CIGlobals

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.controls.ControlManager import CollisionHandlerRayStart

class ShadowPlacer:
	notify = directNotify.newCategory("ShadowPlacer")

	def __init__(self, shadow_node, mat):
		self.setup_shadow_ray(shadow_node, mat)

	def setup_shadow_ray(self, shadow_node, mat):
		ray = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
		ray_node = CollisionNode("ray_node")
		ray_node.add_solid(ray)
		self.ray_np = shadow_node.attach_new_node(ray_node)
		self.ray_np.node().set_from_collide_mask(CIGlobals.FloorBitmask)
		self.ray_np.node().set_into_collide_mask(BitMask32.allOff())

		floor_offset = 0.025
		lifter = CollisionHandlerFloor()
		lifter.set_offset(floor_offset)
		lifter.set_reach(4.0)

		lifter.add_collider(self.ray_np, shadow_node)
		if not mat:
			base.cTrav.add_collider(self.ray_np, lifter)

	def delete_shadow_ray(self):
		if hasattr(self, 'ray_np'):
			self.ray_np.remove_node()
			del self.ray_np
		return

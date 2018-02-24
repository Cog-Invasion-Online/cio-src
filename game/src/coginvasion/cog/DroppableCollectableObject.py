"""

  Filename: DroppableCollectableObject.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject
from direct.controls.ControlManager import CollisionHandlerRayStart
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerFloor, BitMask32, ModelPool, TexturePool
from src.coginvasion.globals import CIGlobals

class DroppableCollectableObject(DirectObject, NodePath):
	notify = directNotify.newCategory("DroppableCollectableObject")
	
	def __init__(self):
		NodePath.__init__(self, 'droppableCollectableObject')
		self.collSensorNodePath = None
		self.collRayNodePath = None
		
	def loadObject(self):
		# Should be overridden by a child class.
		pass
		
	def removeObject(self):
		# Should be overridden by a child class.
		pass
		
	def loadCollisions(self):
		sphere = CollisionSphere(0, 0, 0, 1)
		sphere.setTangible(0)
		node = CollisionNode('objectCollNode')
		node.addSolid(sphere)
		node.setCollideMask(CIGlobals.WallBitmask)
		self.collSensorNodePath = self.attachNewNode(node)
		
		ray = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
		rayNode = CollisionNode('objectRayNode')
		rayNode.addSolid(ray)
		rayNode.setFromCollideMask(CIGlobals.FloorBitmask)
		rayNode.setIntoCollideMask(BitMask32.allOff())
		self.collRayNodePath = self.attachNewNode(rayNode)
		lifter = CollisionHandlerFloor()
		lifter.addCollider(self.collRayNodePath, self)
		base.cTrav.addCollider(self.collRayNodePath, lifter)
		
	def removeCollisions(self):
		if self.collSensorNodePath:
			self.collSensorNodePath.removeNode()
			self.collSensorNodePath = None
		if self.collRayNodePath:
			self.collRayNodePath.removeNode()
			self.collRayNodePath = None
		
	def load(self):

		self.loadObject()
		self.loadCollisions()
		
	def unload(self):
		self.removeCollisions()
		self.removeObject()
		self.removeNode()
		ModelPool.garbageCollect()
		TexturePool.garbageCollect()
		

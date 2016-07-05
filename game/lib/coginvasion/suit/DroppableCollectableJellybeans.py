"""

  Filename: DroppableCollectableJellybeans.py
  Created by: blach (22Mar15)

"""
from direct.directnotify.DirectNotifyGlobal import directNotify
from DroppableCollectableObject import DroppableCollectableObject

class DroppableCollectableJellybeans(DroppableCollectableObject):
	notify = directNotify.newCategory("DroppableCollectableJellybeans")
	
	def __init__(self):
		DroppableCollectableObject.__init__(self)
		
	def unload(self):
		self.collectSfx = None
		DroppableCollectableObject.unload(self)

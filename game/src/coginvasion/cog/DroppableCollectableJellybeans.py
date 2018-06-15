"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DroppableCollectableJellybean.py
@author Brian Lach
@date March 22, 2015

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

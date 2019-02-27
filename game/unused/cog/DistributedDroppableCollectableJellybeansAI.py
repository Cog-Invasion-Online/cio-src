"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDroppableCollectableJellybeansAI.py
@author Brian Lach
@date March 22, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableObjectAI import DistributedDroppableCollectableObjectAI

class DistributedDroppableCollectableJellybeansAI(DistributedDroppableCollectableObjectAI):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeansAI")
	
	def __init__(self, air):
		DistributedDroppableCollectableObjectAI.__init__(self, air)
		self.value = 0
		
	def setValue(self, value):
		self.value = value
		
	def getValue(self):
		return self.value
		
	def collectedObject(self):
		avId = self.air.getAvatarIdFromSender()
		avatar = self.air.doId2do.get(avId)
		if avatar:
			avatar.b_setMoney(avatar.getMoney() + self.getValue())
		DistributedDroppableCollectableObjectAI.collectedObject(self)
		
	def delete(self):
		self.value = None
		DistributedDroppableCollectableObjectAI.delete(self)

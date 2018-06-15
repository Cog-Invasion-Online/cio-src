"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDroppableCollectableJellybeanJarAI.py
@author Brian Lach
@date March 22, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeansAI import DistributedDroppableCollectableJellybeansAI

class DistributedDroppableCollectableJellybeanJarAI(DistributedDroppableCollectableJellybeansAI):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeanJarAI")
	
	def __init__(self, air):
		DistributedDroppableCollectableJellybeansAI.__init__(self, air)

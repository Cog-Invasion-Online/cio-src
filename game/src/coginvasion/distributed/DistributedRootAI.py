"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedRootAI.py
@author Brian Lach
@date December 04, 2014

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedRootAI(DistributedObjectAI):
	notify = directNotify.newCategory("DistributedRootAI")
	
	def setParentingRules(self, todo0, todo1):
		pass

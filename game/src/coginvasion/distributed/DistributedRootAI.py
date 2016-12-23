########################################
# Filename: DistributedRootAI.py
# Created by: blach (04Dec14)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedRootAI(DistributedObjectAI):
	notify = directNotify.newCategory("DistributedRootAI")
	
	def setParentingRules(self, todo0, todo1):
		pass

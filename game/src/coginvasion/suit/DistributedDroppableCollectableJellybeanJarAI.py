"""

  Filename: DistributedDroppableCollectableJellybeanJarAI.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeansAI import DistributedDroppableCollectableJellybeansAI

class DistributedDroppableCollectableJellybeanJarAI(DistributedDroppableCollectableJellybeansAI):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeanJarAI")
	
	def __init__(self, air):
		DistributedDroppableCollectableJellybeansAI.__init__(self, air)

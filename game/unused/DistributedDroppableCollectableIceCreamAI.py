"""

  Filename: DistributedDroppableCollectableIceCreamAI.py
  Created by: blach (03Apr15)

"""

from DistributedDroppableCollectableHealthAI import DistributedDroppableCollectableHealthAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedDroppableCollectableIceCreamAI(DistributedDroppableCollectableHealthAI):
    notify = directNotify.newCategory("DistributedDroppableCollectableIceCreamAI")
    
    def __init__(self, air):
        DistributedDroppableCollectableHealthAI.__init__(self, air)
        self.health = 10

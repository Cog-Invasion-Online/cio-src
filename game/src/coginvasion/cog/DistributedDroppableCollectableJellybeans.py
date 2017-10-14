"""

  Filename: DistributedDroppableCollectableJellybeans.py
  Created by: blach (22Mar15)
  
"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import SoundInterval
from DistributedDroppableCollectableObject import DistributedDroppableCollectableObject

class DistributedDroppableCollectableJellybeans(DistributedDroppableCollectableObject):
    notify = directNotify.newCategory("DistributedDroppableCollectableJellybeans")
    
    def __init__(self, cr):
        DistributedDroppableCollectableObject.__init__(self, cr)
    
    # Use wait to delay the actual delete of the object.
    def handleCollisions(self, avId, wait = 0):
        SoundInterval(self.collectSfx).start()
        DistributedDroppableCollectableObject.handleCollisions(self, avId, wait)
        
    def unload(self):
        self.collectSfx = None
        DistributedDroppableCollectableObject.unload(self)
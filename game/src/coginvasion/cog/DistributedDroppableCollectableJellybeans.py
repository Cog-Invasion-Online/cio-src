"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDroppableCollectableJellybeans.py
@author Brian Lach
@date March 22, 2015

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
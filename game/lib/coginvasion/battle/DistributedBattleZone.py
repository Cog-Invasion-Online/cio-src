########################################
# Filename: DistributedBattleZone.py
# Created by: DecodedLogic (25Jul16)
########################################

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedBattleZone(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleZone')
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.avIds = []
        
    def disable(self):
        DistributedObject.disable(self)
        self.reset()
        
    def setAvatars(self, avIds):
        self.avIds = avIds
    
    def getAvatars(self):
        return self.avIds
    
    def reset(self):
        self.avIds = []
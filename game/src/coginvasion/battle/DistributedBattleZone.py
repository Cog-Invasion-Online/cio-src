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
        self.suits = {}

    def announceGenerate(self):
        self.accept('suitCreate', self.__handleSuitCreate)
        self.accept('suitDelete', self.__handleSuitDelete)

    def __handleSuitCreate(self, obj):
        self.suits[obj.doId] = obj

    def __handleSuitDelete(self, obj):
        if self.suits.has_key(obj.doId):
            del self.suits[obj.doId]
        
    def disable(self):
        DistributedObject.disable(self)
        self.ignore('suitCreate')
        self.ignore('suitDelete')
        self.reset()
        
    def setAvatars(self, avIds):
        self.avIds = avIds
    
    def getAvatars(self):
        return self.avIds
    
    def reset(self):
        self.avIds = []
        self.suits = {}
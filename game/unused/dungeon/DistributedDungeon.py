########################################
# Filename: DistributedDungeon.py
# Created by: DecodedLogic (14Aug15)
########################################

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedDungeon(DistributedObject):
    notify = directNotify.newCategory('DistributedDungeon')
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        
        # This is a list of the occupants of this dungeon.
        self.occupants = []
        
    def generate(self):
        DistributedObject.generate(self)
        
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        
    def addOccupant(self, occupant):
        if not occupant in self.occupants:
            self.occupants.append(occupant)
        else:
            self.notify.error('Attempted to add an occupant that was already in the dungeon.')
            
    def removeOccupant(self, occupant):
        self.occupants.remove(occupant)
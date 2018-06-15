"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedPlayerToonUD.py
@author Maverick Liberty
@date June 15, 2018

"""

from direct.distributed.DistributedObjectUD import DistributedObjectUD

class DistributedPlayerToonUD(DistributedObjectUD):
    
    def __init__(self, air):
        try:
            self.DistributedPlayerToonUD_initialized
            return
        except:
            self.DistributedPlayerToonUD_initialized = 1
        DistributedObjectUD.__init__(self, air)
        return
        
    def setDNAStrand(self, dnaStrand):
        pass
    
    def setName(self, name):
        pass
        
    def setHealth(self, health):
        pass
        
    def setAnimState(self, anim, ts = 0):
        pass
        
    def setPlace(self, place):
        pass

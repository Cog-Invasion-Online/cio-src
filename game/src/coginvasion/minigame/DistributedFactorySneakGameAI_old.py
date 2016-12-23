"""

  Filename: DistributedFactorySneakGameAI.py
  Created by: mliberty (30Mar15)
    
"""

import DistributedMinigameAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedFactorySneakGameAI(DistributedMinigameAI.DistributedMinigameAI):
    notify = directNotify.newCategory("DistributedFactorySneakGameAI")
    
    def __init__(self, air):
        try:
            self.DistributedFactorySneakGameAI_initalized
            return
        except:
            self.DistributedFactorySneakGameAI_initalized = 1
        DistributedMinigameAI.DistributedMinigameAI.__init__(self, air)
            
        
    

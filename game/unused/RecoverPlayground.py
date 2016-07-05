"""

  Filename: RecoverPlayground.py
  Created by: blach (03Apr15)

"""

import Playground
from direct.directnotify.DirectNotifyGlobal import directNotify

class RecoverPlayground(Playground.Playground):
    notify = directNotify.newCategory("RecoverPlayground")
    
    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        
    """    
    def enterWalk(self, teleportIn = 0):
        Playground.Place.Place.enterWalk(self, teleportIn)
        
    def exitWalk(self):
        Playground.Place.Place.exitWalk(self)
    """

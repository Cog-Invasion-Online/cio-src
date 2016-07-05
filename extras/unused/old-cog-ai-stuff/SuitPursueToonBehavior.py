# Filename: SuitPursueToonBehavior.py
# Created by:  blach (26Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from SuitPathBehavior import SuitPathBehavior
import SuitPathFinder

class SuitPursueToonBehavior(SuitPathBehavior):
    notify = directNotify.newCategory('SuitPursueToonBehavior')
    
    def __init__(self, suit):
        SuitPathBehavior.__init__(self, suit)
    

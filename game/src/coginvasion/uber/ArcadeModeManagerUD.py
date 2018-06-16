"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ArcadeModeManagerUD.py
@author Maverick Liberty
@date June 15, 2018

This is the manager for the Arcade Mode matches

"""

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify

from string import ascii_letters, digits
from random import choice

class ArcadeModeManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('ArcadeModeManagerUD')
    
    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        
        # Dictionary containing all the active sessions.
        self.sessions = {}
        
    def generateSessionCode(self, length=4):
        """ Generates a random session code using the upper and lowercase letters and numbers """
        code = ''.join(choice(ascii_letters + digits) for _ in range(length))
        return code

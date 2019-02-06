"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PublicWalk.py
@author Brian Lach
@date December 15, 2014

@desc PublicWalk is used for avatar movement in public areas such
      as playgrounds. All it does it inherit from Walk and enable
      the shticker book, laff meter, and Gag throwing when we
      enter the StateData.

"""

import Walk
from direct.directnotify.DirectNotifyGlobal import directNotify

class PublicWalk(Walk.Walk):
    notify = directNotify.newCategory("PublicWalk")

    def __init__(self, parentFSM, doneEvent):
        Walk.Walk.__init__(self, doneEvent)
        self.parentFSM = parentFSM

    def enter(self, wantMouse = 0):
        base.localAvatar.startPlay(gags = base.localAvatar.battleControls or base.config.GetBool("want-playground-gags", False),
                                   book = True, laff = True, friends = True, chat = True, wantMouse = wantMouse)

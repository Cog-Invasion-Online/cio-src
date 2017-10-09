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

    def enter(self):
        Walk.Walk.enter(self)
        base.localAvatar.showBookButton()
        base.localAvatar.createLaffMeter()

        if base.localAvatar.inBattle or base.config.GetBool("want-playground-gags", False):
            base.localAvatar.enableGags(1)

        base.localAvatar.createMoney()
        
        if not base.localAvatar.GTAControls:
            self.acceptOnce('escape-up', base.localAvatar.bookButtonClicked)

    def exit(self):
        Walk.Walk.exit(self)
        
        if not base.localAvatar.GTAControls:
            self.ignore('escape-up')
            
        base.localAvatar.hideBookButton()
        base.localAvatar.disableLaffMeter()

        if base.localAvatar.inBattle or base.config.GetBool("want-playground-gags", False):
            base.localAvatar.disableGags()

        base.localAvatar.disableMoney()

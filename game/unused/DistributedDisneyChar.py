# Filename: DistributedDisneyChar.py
# Created by:  blach (01Nov15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNode import DistributedNode
from direct.fsm import ClassicFSM, State

import Char

class DistributedDisneyChar(DistributedNode, Char.Char):
    notify = directNotify.newCategory('DistributedDisneyChar')

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        Char.Char.__init__(self)
        self.fsm = ClassicFSM.ClassicFSM('DistributedDisneyChar', [State.State('off', self.enterOff, self.exitOff),
         State.State('walking', self.enterWalking, self.exitWalking),
         State.State('')])

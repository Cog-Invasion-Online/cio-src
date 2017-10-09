"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedCogOfficeElevatorAI.py
@author Brian Lach
@date December 15, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedElevatorAI import DistributedElevatorAI
from ElevatorConstants import *

class DistributedCogOfficeElevatorAI(DistributedElevatorAI):
    notify = directNotify.newCategory('DistributedCogOfficeElevatorAI')

    # In this class, self.bldg is the DistributedCogOfficeBattleAI associated with this elevator.

    def __init__(self, air, battle, index, eType = ELEVATOR_NORMAL):
        DistributedElevatorAI.__init__(self, air, battle, 0, eType)
        self.index = index
        
    def closingTask(self, task):
        if self.index == 1:
            self.bldg.b_setAvatars(self.getSortedAvatarList())
            self.slotTakenByAvatarId = {}
        self.b_setState('closed')
        return task.done

    def getIndex(self):
        return self.index

    def delete(self):
        self.index = None
        DistributedElevatorAI.delete(self)

"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedCogOfficeElevatorAI.py
@author Brian Lach
@date December 15, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedElevatorAI import DistributedElevatorAI
from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI
from ElevatorConstants import *

class DistributedCogOfficeElevatorAI(DistributedElevatorAI, DistributedEntityAI):
    notify = directNotify.newCategory('DistributedCogOfficeElevatorAI')

    # In this class, self.bldg is the DistributedCogOfficeBattleAI associated with this elevator.

    def __init__(self, air, battle, eType = ELEVATOR_NORMAL):
        DistributedElevatorAI.__init__(self, air, battle, 0, eType)
        DistributedEntityAI.__init__(self, air, battle)
        self.index = 0
        
    def loadEntityValues(self):
        self.index = self.getEntityValueInt("index")
        self.type = self.index

    def enterClosing(self):
        base.taskMgr.doMethodLater(ElevatorData[self.type]['closeTime'], self.closingTask, self.uniqueName('closingTask'))
        if self.index == 1:
            self.bldg.b_setAvatars(self.getSortedAvatarList())

    def closingTask(self, task):
        if self.index == 1:
            self.slotTakenByAvatarId = {}
        self.b_setState('closed')
        return task.done

    def getIndex(self):
        return self.index

    def delete(self):
        base.taskMgr.remove(self.uniqueName('closingTask'))
        self.index = None
        DistributedElevatorAI.delete(self)
        DistributedEntityAI.delete(self)

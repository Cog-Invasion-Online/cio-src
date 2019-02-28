"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedCogOfficeSuit.py
@author Brian Lach
@date December 17, 2015

"""

from panda3d.core import Point3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State

from src.coginvasion.npc.NPCWalker import NPCWalkInterval
from src.coginvasion.cog.DistributedSuit import DistributedSuit
from CogOfficeConstants import *

class DistributedCogOfficeSuit(DistributedSuit):
    notify = directNotify.newCategory('DistributedCogOfficeSuit')

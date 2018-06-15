"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTailorNPCToonAI.py
@author Maverick Liberty
@date August 11, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
import DistributedNPCToonAI

class DistributedTailorNPCToonAI(DistributedNPCToonAI.DistributedNPCToonAI):
    notify = directNotify.newCategory('DistributedTailorToonAI')
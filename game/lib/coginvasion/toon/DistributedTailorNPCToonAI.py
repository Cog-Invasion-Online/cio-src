# Filename: DistributedTailorNPCToonAI.py
# Created by:  DecodedLogic (11Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
import DistributedNPCToonAI

class DistributedTailorNPCToonAI(DistributedNPCToonAI.DistributedNPCToonAI):
    notify = directNotify.newCategory('DistributedTailorToonAI')
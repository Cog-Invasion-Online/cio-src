# Filename: DistributedFactorySneakGameAI.py
# Created by:  blach (21Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedToonFPSGameAI import DistributedToonFPSGameAI

class DistributedFactorySneakGameAI(DistributedToonFPSGameAI):
    notify = directNotify.newCategory("DistributedFactorySneakGameAI")

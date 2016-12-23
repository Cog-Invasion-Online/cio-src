# Filename: DistrictNameManager.py
# Created by:  blach (23Jul15)

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistrictNameManager(DistributedObjectGlobal):
    notify = directNotify.newCategory("DistrictNameManager")

"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagShopInteriorAI.py
@author Brian Lach
@date November 06, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.hood import DistributedToonInteriorAI

class DistributedGagShopInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):
    notify = directNotify.newCategory('DistributedGagShopInteriorAI')

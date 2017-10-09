"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CTHoodAI.py
@author Brian Lach
@date August 14, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.hood import HoodAI
from src.coginvasion.globals import CIGlobals
import DistributedCityCartAI

class CTHoodAI(HoodAI.HoodAI):
    notify = directNotify.newCategory('CTHoodAI')

    MaxCarts = 6

    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air, CIGlobals.CogTropolisId, CIGlobals.CogTropolis)
        self.carts = []
        self.startup()

    def startup(self):
        self.dnaFiles = []
        for i in range(self.MaxCarts):
            cart = DistributedCityCartAI.DistributedCityCartAI(self.air, i)
            cart.generateWithRequired(self.zoneId)
            cart.b_setParent(CIGlobals.SPRender)
            self.carts.append(cart)
        HoodAI.HoodAI.startup(self)

    def shutdown(self):
        for cart in self.carts:
            cart.requestDelete()
        del self.carts
        HoodAI.HoodAI.shutdown(self)

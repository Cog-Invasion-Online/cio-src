"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLHood.py
@author Brian Lach
@date July 24, 2015

"""

from panda3d.core import PolylightEffect, VBase4

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
from playground.DLSafeZoneLoader import DLSafeZoneLoader
from street.DLTownLoader import DLTownLoader
from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType

class DLHood(ToonHood):
    notify = directNotify.newCategory("DLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.DonaldsDreamland
        self.safeZoneLoader = DLSafeZoneLoader
        self.townLoader = DLTownLoader
        self.abbr = "DL"
        self.storageDNAFile = "phase_8/dna/storage_DL.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_8/dna/winter_storage_DL.pdna"
        self.titleColor = (0.443, 0.21, 1.0, 1.0)
        self.loaderDoneEvent = 'DLHood-loaderDone'

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('DLHood').addChild(self.fsm)

        render.setEffect(PolylightEffect.make())

    def unload(self):
        self.parentFSM.getStateNamed('DLHood').removeChild(self.fsm)
        render.clearEffect(PolylightEffect.getClassType())
        ToonHood.unload(self)

"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonHood.py
@author Brian Lach
@date December 14, 2014

"""

from panda3d.core import Vec4

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

import Hood

class ToonHood(Hood.Hood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        Hood.Hood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.safeZoneLoader = None
        self.townLoader = None
        self.fsm = ClassicFSM('Hood', [State('off', self.enterOff, self.exitOff),
                    State('safeZoneLoader', self.enterSafeZoneLoader,
                        self.exitSafeZoneLoader, ['quietZone', 'townLoader']),
                    State('townLoader', self.enterTownLoader,
                        self.exitTownLoader, ['quietZone', 'safeZoneLoader']),
                    State('quietZone', self.enterQuietZone, self.exitQuietZone,
                        ['safeZoneLoader', 'townLoader'])],
                    'off', 'off')
        self.fsm.enterInitialState()
        return

    def loadLoader(self, requestStatus):
        loader = requestStatus['loader']
        if loader == 'safeZoneLoader':
            if self.safeZoneLoader:
                self.loader = self.safeZoneLoader(self, self.fsm.getStateNamed('safeZoneLoader'), self.loaderDoneEvent)
                self.loader.load()
            else:
                self.notify.error('ToonHood.ToonHood.safeZoneLoader cannot be None!' % loader)
        elif loader == 'townLoader':
            if self.townLoader:
                self.loader = self.townLoader(self, self.fsm.getStateNamed('townLoader'), self.loaderDoneEvent)
                self.loader.load(requestStatus['zoneId'])
        else:
            self.notify.error('Unknown loader %s!' % loader)

    def enterTownLoader(self, requestStatus):
        self.acceptOnce(self.loaderDoneEvent, self.handleTownLoaderDone)
        self.loader.enter(requestStatus)
        self.spawnTitleText(requestStatus['zoneId'])

    def exitTownLoader(self):
        taskMgr.remove('titleText')
        self.hideTitleText()
        self.ignore(self.loaderDoneEvent)
        self.loader.exit()
        self.loader.unload()
        del self.loader

    def handleTownLoaderDone(self):
        doneStatus = self.loader.getDoneStatus()
        if self.isSameHood(doneStatus):
            self.fsm.request('quietZone', [doneStatus])
        else:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)

    def load(self):
        Hood.Hood.load(self)
        self.whiteFogColor = Vec4(0.80000000000000004, 0.80000000000000004, 0.80000000000000004, 1)
        self.underwaterFogColor = Vec4(0.0, 0.0, 0.59999999999999998, 1.0)

    def unload(self):
        del self.safeZoneLoader
        Hood.Hood.unload(self)

    def enter(self, requestStatus):
        self.loadLoader(requestStatus)
        Hood.Hood.enter(self, requestStatus)

    def exit(self):
        Hood.Hood.exit(self)

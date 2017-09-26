"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIBase.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import loadPrcFile, NodePath

from direct.showbase.ShowBase import ShowBase
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.manager.UserInputStorage import UserInputStorage
from src.coginvasion.globals import CIGlobals
from CubeMapManager import CubeMapManager

import __builtin__

if game.usepipeline:
    from rpcore import RenderPipeline

class CIBase(ShowBase):
    notify = directNotify.newCategory("CIBase")

    def __init__(self):

        if game.usepipeline:
            self.pipeline = RenderPipeline()
            self.pipeline.create(self)
        else:
            ShowBase.__init__(self)

        uis = UserInputStorage()
        self.inputStore = uis
        self.userInputStorage = uis
        __builtin__.inputStore = uis
        __builtin__.userInputStorage = uis

        cbm = CubeMapManager()
        self.cubeMapMgr = cbm
        __builtin__.cubeMapMgr = cbm

    def saveCubeMap(self, namePrefix = 'cube_map_#.jpg', size = 256):
        # Hide all objects from our cubemap.
        if hasattr(self, 'cr'):
            for do in self.cr.doId2do.values():
                if isinstance(do, NodePath):
                    do.hide()

        ShowBase.saveCubeMap(self, namePrefix, size = size)

        # Reshow the objects.
        if hasattr(self, 'cr'):
            for do in self.cr.doId2do.values():
                if isinstance(do, NodePath):
                    do.show()

    def setTimeOfDay(self, time):
        if game.usepipeline:
            self.pipeline.daytime_mgr.time = time

    def doOldToontownRatio(self):
        ShowBase.adjustWindowAspectRatio(self, 4. / 3.)

    def doRegularRatio(self):
        ShowBase.adjustWindowAspectRatio(self, self.getAspectRatio())

    def adjustWindowAspectRatio(self, aspectRatio):
        if (CIGlobals.getSettingsMgr() is None):
            return

        if (CIGlobals.getSettingsMgr().getSetting("maspr") is True):
            # Go ahead and maintain the aspect ratio if the user wants us to.
            ShowBase.adjustWindowAspectRatio(self, aspectRatio)
        else:
            # The user wants us to keep a 4:3 ratio no matter what (old toontown feels).
            self.doOldToontownRatio()

    def muteMusic(self):
        self.musicManager.setVolume(0.0)

    def unMuteMusic(self):
        self.musicManager.setVolume(CIGlobals.SettingsMgr.getSetting("musvol"))

    def muteSfx(self):
        self.sfxManagerList[0].setVolume(0.0)

    def unMuteSfx(self):
        self.sfxManagerList[0].setVolume(CIGlobals.SettingsMgr.getSetting("sfxvol"))

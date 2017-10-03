"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIBase.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import loadPrcFile, NodePath, PGTop

from direct.showbase.ShowBase import ShowBase
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.manager.UserInputStorage import UserInputStorage
from src.coginvasion.globals import CIGlobals
from CubeMapManager import CubeMapManager
from WaterReflectionManager import WaterReflectionManager

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

        wrm = WaterReflectionManager()
        self.waterReflectionMgr = wrm
        __builtin__.waterReflectionMgr = wrm

        self.credits2d = self.render2d.attachNewNode(PGTop("credits2d"))
        self.credits2d.setScale(1.0 / self.getAspectRatio(), 1.0, 1.0)

        self.wakeWaterHeight = -30.0

    def saveCubeMap(self, namePrefix = 'cube_map_#.jpg', size = 1024):
        namePrefix = raw_input("Cube map file: ")

        base.localAvatar.stopSmooth()
        base.localAvatar.setHpr(0, 0, 0)

        # Hide all objects from our cubemap.
        if hasattr(self, 'cr'):
            for do in self.cr.doId2do.values():
                if isinstance(do, NodePath):
                    do.hide()

        print "Cube map position:", camera.getPos(render)

        ShowBase.saveCubeMap(self, namePrefix, size = size)

        # Reshow the objects.
        if hasattr(self, 'cr'):
            for do in self.cr.doId2do.values():
                if isinstance(do, NodePath):
                    do.show()

        base.localAvatar.startSmooth()

    def setTimeOfDay(self, time):
        if game.usepipeline:
            self.pipeline.daytime_mgr.time = time

    def doOldToontownRatio(self):
        ShowBase.adjustWindowAspectRatio(self, 4. / 3.)
        self.credits2d.setScale(1.0 / (4. / 3.), 1.0, 1.0)

    def doRegularRatio(self):
        ShowBase.adjustWindowAspectRatio(self, self.getAspectRatio())

    def adjustWindowAspectRatio(self, aspectRatio):
        if (CIGlobals.getSettingsMgr() is None):
            return

        if (CIGlobals.getSettingsMgr().getSetting("maspr") is True):
            # Go ahead and maintain the aspect ratio if the user wants us to.
            ShowBase.adjustWindowAspectRatio(self, aspectRatio)
            self.credits2d.setScale(1.0 / aspectRatio, 1.0, 1.0)
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

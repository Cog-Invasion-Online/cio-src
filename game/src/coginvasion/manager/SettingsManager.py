"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SettingsManager.py
@author Brian Lach
@date July ??, 2014

"""

from panda3d.core import AntialiasAttrib, TextureStage
from panda3d.core import loadPrcFileData, WindowProperties
from direct.directnotify.DirectNotify import DirectNotify

import json

notify = DirectNotify().newCategory("SettingsManager")

class SettingsManager:
    MouseCursors = {"None": "", "Toontown": game.phasedir + "toonmono.cur"}

    def __init__(self):
        self.jsonData = None
        self.jsonFile = None
        self.jsonFilename = None

    def loadFile(self, jsonfile):
        self.jsonFilename = jsonfile
        self.jsonFile = open(self.jsonFilename)
        self.jsonData = json.load(self.jsonFile)

    def applySettings(self):
        settings = self.jsonData["settings"]

        # Game screen resolution
        res = settings.get("resolution", None)
        if res == None:
            res = self.updateAndWriteSetting("resolution", (640, 480))

        # Fullscreen toggle
        fs = settings.get("fullscreen", None)
        if fs == None:
            fs = self.updateAndWriteSetting("fs", False)

        # music toggle
        music = settings.get("music", None)
        if music == None:
            music = self.updateAndWriteSetting("music", True)

        # music volume
        musvol = settings.get("musvol", None)
        if musvol == None:
            musvol = self.updateAndWriteSetting("musvol", 0.65)

        # sfx toggle
        sfx = settings.get("sfx", None)
        if sfx == None:
            sfx = self.updateAndWriteSetting("sfx", True)

        # sfx volume
        sfxvol = settings.get("sfxvol", None)
        if sfxvol == None:
            sfxvol = self.updateAndWriteSetting("sfxvol", 1.0)

        # texture quality
        tex_detail = settings.get("texture-detail", None)
        if tex_detail == None:
            tex_detail = self.updateAndWriteSetting("texture-detail", "high")

        # model quality
        model_detail = settings.get('model-detail', None)
        if model_detail == None:
            model_detail = self.updateAndWriteSetting('model-detail', "high")

        # Antialiasing
        aa = settings.get("aa", None)
        if aa == None:
            aa = self.updateAndWriteSetting("aa", 0)

        # Anisotropic filtering/degree
        af = settings.get("af", None)
        if af == None:
            af = self.updateAndWriteSetting("af", 0)
            
        shadows = settings.get("shadows", None)
        if shadows == None:
            shadows = self.updateAndWriteSetting("shadows", 0)

        # Chat sounds
        chs = settings.get("chs", None)
        if chs == None:
            chs = self.updateAndWriteSetting("chs", True)

        # General gameplay FOV
        genfov = settings.get("genfov", None)
        if genfov == None:
            genfov = self.updateAndWriteSetting("genfov", 52.0)

        # First person minigame FOV
        fpmgfov = settings.get("fpmgfov", None)
        if fpmgfov == None:
            fpmgfov = self.updateAndWriteSetting("fpmgfov", 70.0)

        # First person minigame mouse sensitivity
        fpmgms = settings.get("fpmgms", None)
        if fpmgms == None:
            fpmgms = self.updateAndWriteSetting("fpmgms", 0.1)

        # Gag key
        gagkey = settings.get("gagkey", None)
        if gagkey == None:
            gagkey = self.updateAndWriteSetting("gagkey", "alt")

        # Maintain aspect ratio
        maspr = settings.get("maspr", None)
        if maspr == None:
            maspr = self.updateAndWriteSetting("maspr", True)
            
        cursor = settings.get("cursor", None)
        if cursor == None:
            cursor = self.updateAndWriteSetting("cursor", SettingsManager.MouseCursors.keys()[0])

        base.enableMusic(music)
        base.enableSoundEffects(sfx)

        base.musicManager.setVolume(musvol)
        base.sfxManagerList[0].setVolume(sfxvol)

        if aa != 0:
            render.set_antialias(AntialiasAttrib.MMultisample)
            aspect2d.set_antialias(AntialiasAttrib.MMultisample)
        else:
            render.clear_antialias()
            aspect2d.clear_antialias()

        print "Anisotropic degree of {0}".format(af)
        loadPrcFileData("", "texture-anisotropic-degree {0}".format(af))

        if tex_detail == "high":
            pass
        elif tex_detail == "low":
            loadPrcFileData("", "compressed-textures 1")

        from src.coginvasion.globals import CIGlobals

        CIGlobals.DefaultCameraFov = genfov
        CIGlobals.GunGameFov = fpmgfov

        wp = WindowProperties()
        wp.setSize(res[0], res[1])
        wp.setFullscreen(fs)
        wp.setCursorFilename(SettingsManager.MouseCursors[cursor])
        base.win.requestProperties(wp)

    def maybeFixAA(self):
        if self.getSetting("aa") == 0:
            print "Fixing anti-aliasing..."
            loadPrcFileData('', 'framebuffer-multisample 0')
            loadPrcFileData('', 'multisamples 0')
        else:
            loadPrcFileData('', 'framebuffer-multisample 1')
            loadPrcFileData('', 'multisamples ' + str(self.getSetting("aa")))

    def getSetting(self, setting):
        return self.jsonData["settings"][setting]

    def getSettings(self):
        return self.jsonData["settings"]

    def updateAndWriteSetting(self, setting, value, apply=0):
        self.jsonData["settings"][setting] = value

        jsonFile = open(self.jsonFilename, "w+")
        jsonFile.write(json.dumps(self.jsonData, indent = 4))
        jsonFile.close()

        if apply:
            wp = WindowProperties()
            if setting == "resolution":
                width, height = value
                wp.setSize(width, height)
            elif setting == "fullscreen":
                wp.setFullscreen(value[0])
            base.win.requestProperties(wp)

        return value

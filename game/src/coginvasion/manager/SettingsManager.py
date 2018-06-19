"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SettingsManager.py
@author Brian Lach
@date July ??, 2014

"""

from panda3d.core import AntialiasAttrib
from panda3d.core import LightRampAttrib
from panda3d.core import loadPrcFileData, WindowProperties
from direct.directnotify.DirectNotifyGlobal import directNotify

import json

class SettingsManager:
    MouseCursors = {"None": "", "Toontown": game.phasedir + "toonmono.cur"}
    ReflectionQuality = {"Off": 0, "Low": 256, "Medium": 512, "High": 1024, "Ultra": 2048}
    notify = directNotify.newCategory('SettingsManager')

    def __init__(self):
        self.jsonData = None
        self.jsonFile = None
        self.jsonFilename = None

    def loadFile(self, jsonfile):
        self.jsonFilename = jsonfile
        try:
            self.jsonFile = open(self.jsonFilename)
            self.jsonData = json.load(self.jsonFile)
        except:
            self.jsonData = {}
            self.jsonData["settings"] = {}

    def applySettings(self):
        settings = self.jsonData["settings"]

        # Game screen resolution
        res = settings.get("resolution", None)
        if res is None:
            res = self.updateAndWriteSetting("resolution", (640, 480))

        # Fullscreen toggle
        fs = settings.get("fullscreen", None)
        if fs is None:
            fs = self.updateAndWriteSetting("fullscreen", False)

        # music toggle
        music = settings.get("music", None)
        if music is None:
            music = self.updateAndWriteSetting("music", True)

        # music volume
        musvol = settings.get("musvol", None)
        if musvol is None:
            musvol = self.updateAndWriteSetting("musvol", 0.35)

        # sfx toggle
        sfx = settings.get("sfx", None)
        if sfx is None:
            sfx = self.updateAndWriteSetting("sfx", True)

        # sfx volume
        sfxvol = settings.get("sfxvol", None)
        if sfxvol is None:
            sfxvol = self.updateAndWriteSetting("sfxvol", 1.0)

        # texture quality
        tex_detail = settings.get("texture-detail", None)
        if tex_detail is None:
            tex_detail = self.updateAndWriteSetting("texture-detail", "high")

        # model quality
        model_detail = settings.get('model-detail', None)
        if model_detail is None:
            model_detail = self.updateAndWriteSetting('model-detail', "high")

        # Antialiasing
        aa = settings.get("aa", None)
        if aa is None:
            aa = self.updateAndWriteSetting("aa", 0)

        # Anisotropic filtering/degree
        af = settings.get("af", None)
        if af is None:
            af = self.updateAndWriteSetting("af", 0)
            
        shadows = settings.get("shadows", None)
        if shadows is None:
            shadows = self.updateAndWriteSetting("shadows", 0)

        # Chat sounds
        chs = settings.get("chs", None)
        if chs is None:
            chs = self.updateAndWriteSetting("chs", True)

        # General gameplay FOV
        genfov = settings.get("genfov", None)
        if genfov is None:
            genfov = self.updateAndWriteSetting("genfov", 52.0)

        # First person minigame FOV
        fpmgfov = settings.get("fpmgfov", None)
        if fpmgfov is None:
            fpmgfov = self.updateAndWriteSetting("fpmgfov", 70.0)

        # First person minigame mouse sensitivity
        fpmgms = settings.get("fpmgms", None)
        if fpmgms is None:
            fpmgms = self.updateAndWriteSetting("fpmgms", 0.1)

        # Gag key
        gagkey = settings.get("gagkey", None)
        if gagkey is None:
            gagkey = self.updateAndWriteSetting("gagkey", "mouse1")

        # Maintain aspect ratio
        maspr = settings.get("maspr", None)
        if maspr is None:
            maspr = self.updateAndWriteSetting("maspr", True)
            
        # Lighting
        lighting = settings.get("lighting", None)
        if lighting is None:
            lighting = self.updateAndWriteSetting("lighting", False)
        
        # Mouse cursor
        cursor = settings.get("cursor", None)
        if cursor is None:
            cursor = self.updateAndWriteSetting("cursor", SettingsManager.MouseCursors.keys()[0])
            
        # Hdr
        hdr = settings.get("hdr", None)
        if hdr is None:
            hdr = self.updateAndWriteSetting("hdr", 0)
            
        # Per pixel lighting
        ppl = settings.get("ppl", None)
        if ppl is None:
            ppl = self.updateAndWriteSetting("ppl", False)
            
        # Reflection quality
        refl = settings.get("refl", None)
        if refl is None:
            refl = self.updateAndWriteSetting("refl", "Off")
            
        # FPS Meter
        fps = settings.get("fps", None)
        if fps is None:
            fps = self.updateAndWriteSetting("fps", False)

        # bloom filter
        bloom = settings.get("bloom", None)
        if bloom is None:
            bloom = self.updateAndWriteSetting("bloom", False)

        base.enableMusic(music)
        base.enableSoundEffects(sfx)
        
        from src.coginvasion.globals import CIGlobals
        
        game.uselighting = lighting
        if lighting:
            #render.show(CIGlobals.ShadowCameraBitmask)
            if ppl:
                render.setShaderAuto()
            else:
                render.setShaderOff()

        base.musicManager.setVolume(musvol)
        base.sfxManagerList[0].setVolume(sfxvol)
        
        self.applyHdr(hdr)

        base.setBloom(bloom)

        if aa != 0:
            render.setAntialias(AntialiasAttrib.MMultisample)
            aspect2d.setAntialias(AntialiasAttrib.MMultisample)
        else:
            render.clearAntialias()
            aspect2d.clearAntialias()

        self.notify.info("Anisotropic degree of {0}".format(af))
        loadPrcFileData("", "texture-anisotropic-degree {0}".format(af))

        if tex_detail == "high":
            pass
        elif tex_detail == "low":
            loadPrcFileData("", "compressed-textures 1")

        CIGlobals.DefaultCameraFov = genfov
        CIGlobals.GunGameFov = fpmgfov

        wp = WindowProperties()
        wp.setSize(res[0], res[1])
        wp.setFullscreen(fs)
        wp.setCursorFilename(SettingsManager.MouseCursors[cursor])
        base.win.requestProperties(wp)
        
    def applyHdr(self, hdr):
        if hdr == 1:
            render.setAttrib(LightRampAttrib.makeHdr0())
        elif hdr == 2:
            render.setAttrib(LightRampAttrib.makeHdr1())
        elif hdr == 3:
            render.setAttrib(LightRampAttrib.makeHdr2())
        else:
            render.clearAttrib(LightRampAttrib.getClassType())

    def maybeFixAA(self):
        if self.getSetting("aa") == 0:
            self.notify.info("Fixing anti-aliasing...")
            loadPrcFileData('', 'framebuffer-multisample 0')
            loadPrcFileData('', 'multisamples 0')
        else:
            loadPrcFileData('', 'framebuffer-multisample 1')
            loadPrcFileData('', 'multisamples ' + str(self.getSetting("aa")))

    def getSetting(self, setting):
        return self.jsonData["settings"].get(setting, None)

    def getSettings(self):
        return self.jsonData["settings"]

    def updateAndWriteSetting(self, setting, value, applyChanges=0):
        self.jsonData["settings"][setting] = value

        jsonFile = open(self.jsonFilename, "w+")
        jsonFile.write(json.dumps(self.jsonData, indent = 4))
        jsonFile.close()

        if applyChanges:
            wp = WindowProperties()
            if setting == "resolution":
                width, height = value
                wp.setSize(width, height)
            elif setting == "fullscreen":
                wp.setFullscreen(value[0])
            base.win.requestProperties(wp)

        return value

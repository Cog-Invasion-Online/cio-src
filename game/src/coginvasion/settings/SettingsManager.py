"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SettingsManager.py
@author Maverick Liberty
@date January 20, 2019

"""

from Setting import Setting
from Setting import SHOWBASE_PREINIT, SHOWBASE_POSTINIT
from Setting import DATATYPE_INT, DATATYPE_STR, DATATYPE_TUPLE, DATATYPE_BOOL, DATATYPE_FLOAT

from src.coginvasion.globals import CIGlobals

from panda3d.core import WindowProperties, AntialiasAttrib, loadPrcFileData
from direct.directnotify.DirectNotifyGlobal import directNotify

import json
import os

class SettingsManager:
    notify = directNotify.newCategory('SettingsManager')
    
    MouseCursors = {"Toontown": metadata.PHASE_DIRECTORY + "toonmono.cur", "None": ""}
    ReflectionQuality = {"Off": 0, "Low": 256, "Medium": 512, "High": 1024, "Very High": 2048}
    
    def __init__(self):
        self.jsonData = None
        self.jsonFile = None
        self.jsonFilename = None
        
        # This is a dictionary of the registered settings.
        # Keys are the names of the setting and the value is a "Setting" instance.
        self.registry = {}
        
        self.addSetting("cursor", optionType = DATATYPE_STR, default = self.MouseCursors.keys()[0],
                        callback = self.__updateCursor, sunrise = SHOWBASE_POSTINIT,
                        options = ["Toontown", "None"],
                        description = "Updates the game's cursor.")
        self.addSetting("resolution", optionType = DATATYPE_TUPLE, default = (640, 480), 
                        callback = self.__updateResolution, sunrise = SHOWBASE_PREINIT, 
                        options = ["640x480", "800x600", "1024x768", "1280x720", 
                                   "1360x768", "1366x768", "1600x900", "1920x1080"], 
                        description = "Configures the screen resolution.")
        self.addSetting("maspr", optionType = DATATYPE_BOOL, default = True,
                        callback = self.__updateAspectRatio, sunrise = SHOWBASE_POSTINIT,
                        description = "Maintain aspect ratio?")
        self.addSetting("fullscreen", optionType = DATATYPE_BOOL, default = False,
                        callback = self.__updateFullscreen, sunrise = SHOWBASE_PREINIT,
                        description = "Toggles fullscreen mode.")
        self.addSetting("aa", optionType = DATATYPE_STR, default = "None",
                        callback = self.__updateAA, sunrise = SHOWBASE_PREINIT,
                        options = ["None", "FXAA", "2x MSAA", "4x MSAA", "8x MSAA", "16x MSAA"],
                        description = "Smooths out jagged edges on screen.\nAffects performance.")
        self.addSetting("af", optionType = DATATYPE_INT, default = 0,
                        callback = self.__updateAF, sunrise = SHOWBASE_PREINIT,
                        options = ["None", "x2", "x4", "x8", "x16"],
                        description = "Improves the quality of textures viewed from an angle.\nAffects performance.")
        self.addSetting("vsync", optionType = DATATYPE_BOOL, default = True,
                        callback = self.__updateVsync, sunrise = SHOWBASE_PREINIT,
                        description = "Reduces screen tearing by limiting frame rate to your monitor's refresh rate.\nThis is really only effective in Fullscreen mode.")
        self.addSetting("bloom", optionType = DATATYPE_BOOL, default = False,
                        callback = self.__updateBloom, sunrise = SHOWBASE_POSTINIT, 
                        description = "Increases perceived brightness by glowing objects that are very bright.\nAffects performance.")
        self.addSetting("refl", optionType = DATATYPE_STR, default = "Off",
                        callback = self.__updateWaterReflections, sunrise = SHOWBASE_POSTINIT,
                        options = ["Off", "Low", "Medium", "High", "Very High"],
                        description = 'Sets the resolution of water reflection textures\naround the game. Affects performance.')
        self.addSetting("hdr", optionType = DATATYPE_BOOL, default = True,
                        callback = self.__updateHDR, sunrise = SHOWBASE_POSTINIT,
                        description = "Increases perceived range of colors and brightness on screen.\nRequires at least OpenGL 4.3.'")
        self.addSetting("fps", optionType = DATATYPE_BOOL, default = False,
                        callback = self.__updateFPS, sunrise = SHOWBASE_POSTINIT,
                        description = "Enables/Disables an FPS meter in the top-right\n corner of the screen.")
        self.addSetting("musvol", optionType = DATATYPE_FLOAT, default = 0.25,
                        callback = self.__updateMusicVolume, sunrise = SHOWBASE_POSTINIT,
                        description = "Music Volume"),
        self.addSetting("sfxvol", optionType = DATATYPE_FLOAT, default = 1.0,
                        callback = self.__updateSFXVolume, sunrise = SHOWBASE_POSTINIT,
                        description = "SFX Volume")
        self.addSetting("chs", optionType = DATATYPE_BOOL, default = True,
                        callback = self.__updateChatSounds, sunrise = SHOWBASE_POSTINIT,
                        description = "Toggles chat sound effects.")
        self.addSetting("gagkey", optionType = DATATYPE_STR, default = "mouse1",
                        callback = self.__updateGagKey, sunrise = SHOWBASE_POSTINIT,
                        options = ["mouse1", "f"], description = 'Changes the control to use a gag.')
        self.addSetting("fpmgfov", optionType = DATATYPE_FLOAT, default = 70.0,
                        callback = self.__updateMGFOV, sunrise = SHOWBASE_POSTINIT,
                        description = "Field of View\n(First Person)")
        self.addSetting("fpmgms", optionType = DATATYPE_FLOAT, default = 0.1,
                        callback = self.__updateMouseSensitivity, sunrise = SHOWBASE_POSTINIT,
                        description = "Mouse Sensitivity\n(First Person)")
        self.addSetting("genfov", optionType = DATATYPE_FLOAT, default = 52.0,
                        callback = self.__updateGenFOV, sunrise = SHOWBASE_POSTINIT,
                        description = "Field of View\n(General Gameplay)")
        self.addSetting("resourcePack", optionType = DATATYPE_STR, default = "",
                        callback = self.__updateResourcePack, sunrise = SHOWBASE_POSTINIT,
                        description = "The game's resource pack.")
        self.addSetting("model-detail", optionType = DATATYPE_STR, default = "high",
                        callback = self.__updateModelDetail, sunrise = SHOWBASE_PREINIT,
                        description = "The detail level of models.")
        self.addSetting("texture-detail", optionType = DATATYPE_STR, default = "high",
                        callback = self.__updateTextureDetail, sunrise = SHOWBASE_PREINIT,
                        description = "The detail level of textures.")
        self.addSetting("shadows", optionType = DATATYPE_INT, default = 0,
                        callback = self.__updateShadows, sunrise = SHOWBASE_PREINIT,
                        options = ["Off", "Low", "Medium", "High", "Very High", "Ultra"],
                        description = "The quality of shadows.\nAffects performance.")
        self.addSetting("ao", optionType = DATATYPE_BOOL, default = False,
                        callback = self.__updateAO, sunrise = SHOWBASE_POSTINIT,
                        description = "Screen space ambient occlusion.\nAffects performance")
        self.addSetting("bpov", optionType = DATATYPE_INT, default = 1,
                        callback = self.__updateBattlePOV, sunrise = SHOWBASE_POSTINIT,
                        options = ["Third Person", "First Person"],
                        description = "Battle camera point-of-view.")
    
    def __updateBattlePOV(self, pov):
        try:    base.localAvatar.walkControls.setMode(pov)
        except: pass
                        
    def __updateAO(self, toggle):
        base.setAmbientOcclusion(toggle)
                        
    def __updateShadows(self, shadowIdx):
        csmSizes = [0, 512, 1024, 2048, 4096, 4096]
        cascades = [0, 3,   3,    3,    3,    4]
        if shadowIdx == 0:
            # drop shadows
            loadPrcFileData("", "want-pssm 0")
            metadata.USE_REAL_SHADOWS = 0
        else:
            # real shadows
            loadPrcFileData("", "want-pssm 1")
            loadPrcFileData("", "pssm-size {0}".format(csmSizes[shadowIdx]))
            loadPrcFileData("", "pssm-splits {0}".format(cascades[shadowIdx]))
            metadata.USE_REAL_SHADOWS = 1
            
    
    def __updateCursor(self, cursorName):
        wp = WindowProperties()
        wp.setCursorFilename(self.MouseCursors.get(cursorName))
        base.win.requestProperties(wp)
        
    def updateResolutionAndFullscreen(self, reso, fs):
        """
        This function is required when applying settings from the book,
        as resolution and fullscreen need to be requested together.
        """
        
        wp = WindowProperties()
        wp.setSize(reso[0], reso[1])
        wp.setFullscreen(fs)
        base.win.requestProperties(wp)
        
    def __updateResolution(self, resolutionValue):
        wp = WindowProperties()
        width, height = resolutionValue
        wp.setSize(width, height)

        try:
            base.win.requestProperties(wp)
        except:
            loadPrcFileData("", "win-size {0} {1}".format(width, height))
        
    def __updateAspectRatio(self, maintainRatio):
        if not maintainRatio:
            base.doOldToontownRatio()
        else:
            base.doRegularRatio()
    
    def __updateFullscreen(self, flag):
        wp = WindowProperties()
        wp.setFullscreen(flag)
        
        try:
            base.win.requestProperties(wp)
        except:
            loadPrcFileData("", "fullscreen {0}".format(int(flag)))
    
    def __updateAA(self, degree):
        if "FXAA" in degree:
            # fxaa
            try:    base.setFXAA(True)
            except: pass
        elif "MSAA" in degree:
            degree = int(degree.split('x')[0])
            loadPrcFileData("", "framebuffer-multisample 1")
            loadPrcFileData("", "multisamples {0}".format(degree))
            
            try:
                render.setAntialias(AntialiasAttrib.MMultisample)
                aspect2d.setAntialias(AntialiasAttrib.MMultisample)
            except: pass
        else:
            loadPrcFileData("", "framebuffer-multisample 0")
            loadPrcFileData("", "multisamples 0")
            
            try:
                render.clearAntialias()
                aspect2d.clearAntialias()
            except: pass
            
    def __updateAF(self, degree):
        loadPrcFileData("", "texture-anisotropic-degree {0}".format(degree))
    
    def __updateVsync(self, flag):
        loadPrcFileData("", "sync-video {0}".format(int(flag)))
        
    def __updateBloom(self, flag):
        base.setBloom(flag)
        
    def __updateWaterReflections(self, value):
        # Temporary until water is fixed and optimized
        if value != "Off":
            value = "Off"
            
        qualities = {"Off": 0, "Low": 256, "Medium": 512, "High": 1024, "Very High": 2048}
        resolution = qualities.get(value, 0)
        base.waterReflectionMgr.handleResolutionUpdate(resolution)
        
    def __updateHDR(self, flag):
        base.setHDR(flag)
        
    def __updateFPS(self, flag):
        base.setFrameRateMeter(flag)
        
    def __updateMusicVolume(self, volume):
        base.musicManager.setVolume(volume)
        
    def __updateSFXVolume(self, volume):
        base.sfxManagerList[0].setVolume(volume)
        
    def __updateChatSounds(self, flag):
        pass
    
    def __updateGagKey(self, ctrlName):
        base.inputStore.updateControl('UseGag', ctrlName)
        
        # Let's attempt to update the used key list.
        try:
            base.localAvatar.chatInput.setKeyList()
        except: pass
        
    def __updateMGFOV(self, value):
        CIGlobals.GunGameFov = value
        
    def __updateMouseSensitivity(self, value):
        pass
        
    def __updateGenFOV(self, value):
        CIGlobals.DefaultCameraFov = value
        base.camLens.setMinFov(value / (4. / 3.))
        
    def __updateResourcePack(self, value):
        base.loader.mountMultifiles(value)
        
    def __updateModelDetail(self, value):
        pass
    
    def __updateTextureDetail(self, value):
        pass
        
    def __buildDefaultSettings(self):
        settings = {}
        for settingName in self.registry.keys():
            setting = self.registry.get(settingName)
            settings[settingName] = setting.getDefault()

        return settings
        
    def loadFile(self, jsonFilename):
        """ Loads the JSON file and reads all the currently saved settings.
            Will save default values to the JSON file, if needed.     """

        self.jsonFilename = jsonFilename
        
        if os.path.exists(self.jsonFilename):
            self.jsonFile = open(self.jsonFilename)
            self.jsonData = json.load(self.jsonFile)
            
            settings = self.jsonData["settings"]
            updated = False
            
            for settingName in self.registry.keys():
                setting = self.registry.get(settingName)
                
                fileValue = settings.get(settingName, None)
                
                if fileValue is None:
                    # This means that the setting has no value in the JSON file,
                    # let's set the value to the default.
                    settings[settingName] = setting.getDefault()
                    updated = True
                else:
                    # Let's update the value on the setting class without
                    # calling the callback function.
                    if isinstance(fileValue, list):
                        fileValue = tuple(fileValue)
                    
                    setting.setValue(fileValue, andCallback = False)
            
            if updated:
                self.saveFile()
        else:
            # Settings file not found, save a default file.
            self.jsonData = {}
            self.jsonData["settings"] = self.__buildDefaultSettings()
            self.saveFile()
            
    def saveFile(self):
        """ Saves the current settings to the JSON file """
        
        settings = self.jsonData["settings"]
        
        for settingName in self.registry.keys():
            setting = self.registry.get(settingName)
            
            settings[settingName] = setting.getValue()
        
        jsonFile = open(self.jsonFilename, 'w+')
        jsonFile.write(json.dumps(self.jsonData, indent = 4))
        jsonFile.close()
        
    def addSetting(self, name, optionType, default, callback, sunrise = SHOWBASE_PREINIT, options = None, description = ""):
        if (name and len(name) > 0) and (not name in self.registry.keys()):
            
            if not sunrise in [SHOWBASE_PREINIT, SHOWBASE_POSTINIT]:
                raise ValueError("Invalid sunrise type for Setting %s.".format(name))
            
            if not optionType in [DATATYPE_INT, DATATYPE_STR, DATATYPE_TUPLE, DATATYPE_BOOL, DATATYPE_FLOAT]:
                raise ValueError("Invalid option type for Setting %s.".format(name))
            
            setting = Setting(self, name, optionType, default, 
                              callback, sunrise, options, description)
            
            self.registry.update({name : setting})
        else:
            raise ValueError("You must specify a Setting name!")
        
    def getSetting(self, settingName):
        """ Attempts to fetch a Setting instance by name. Returns None if not found. """
        
        return self.registry.get(settingName, None)
        
    def doSunriseFor(self, sunrise):
        """ Applies settings with the specified sunrise type """
        
        for settingName in self.registry.keys():
            setting = self.registry.get(settingName)
            callback = setting.getCallback()
            
            if setting.getSunrise() == sunrise and callback:
                callback(setting.getValue())
                
        if sunrise == SHOWBASE_POSTINIT:
            if base.config.GetBool("framebuffer-multisample", False):
                render.setAntialias(AntialiasAttrib.MMultisample)
                aspect2d.setAntialias(AntialiasAttrib.MMultisample)
                render2d.setAntialias(AntialiasAttrib.MMultisample)
            else:
                render.clearAntialias()
                aspect2d.clearAntialias()
                render2d.clearAntialias()
            

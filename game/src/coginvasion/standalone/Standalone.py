"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Standalone.py
@author Maverick Liberty
@date November 7, 2015
@desc This is so you can use client objects in a stand-alone program easily.

"""

from panda3d.core import loadPrcFile, loadPrcFileData
from panda3d.core import CullBinManager, AntialiasAttrib
from panda3d.core import UniqueIdAllocator
import __builtin__

from src.coginvasion.base.Metadata import Metadata
__builtin__.metadata = Metadata()
metadata.USE_LIGHTING = 1

loadPrcFile('config/Confauto.prc')
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 0')
loadPrcFileData('', 'multisamples 16')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'egg-load-old-curves 0')
loadPrcFileData('', 'model-path resources')

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

from src.coginvasion.base.CIBase import CIBase
from src.coginvasion.settings.SettingsManager import SettingsManager
from src.coginvasion.settings.Setting import SHOWBASE_PREINIT, SHOWBASE_POSTINIT
jsonFile = "settings.json"
sm = SettingsManager()

from src.coginvasion.globals import CIGlobals
CIGlobals.SettingsMgr = sm
sm.loadFile(jsonFile)
sm.doSunriseFor(sunrise = SHOWBASE_PREINIT)

base = CIBase()
render.setAntialias(AntialiasAttrib.MMultisample)
render.show()

sm.doSunriseFor(sunrise = SHOWBASE_POSTINIT)

base.initStuff()

if metadata.USE_LIGHTING:
    render.setShaderAuto()
else:
    render.clearShader()

from direct.distributed.ClientRepository import ClientRepository
base.cr = ClientRepository(['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
base.cr.isShowingPlayerIds = None
base.cr.doIdAllocator = UniqueIdAllocator(0, 999)

def isChristmas():
    return 0

base.cr.isChristmas = isChristmas

from src.coginvasion.base.CIAudio3DManager import CIAudio3DManager
base.audio3d = CIAudio3DManager(base.sfxManagerList[0], camera)
base.audio3d.setDistanceFactor(25)
base.audio3d.setDropOffFactor(0.025)

from src.coginvasion.nametag import NametagGlobals
from direct.gui import DirectGuiGlobals

DirectGuiGlobals.setDefaultFontFunc(CIGlobals.getToonFont)
DirectGuiGlobals.setDefaultFont(CIGlobals.getToonFont())
DirectGuiGlobals.setDefaultRolloverSound(loader.loadSfx("phase_3/audio/sfx/GUI_rollover.ogg"))
DirectGuiGlobals.setDefaultClickSound(loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.ogg"))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel("phase_3/models/gui/dialog_box_gui.bam"))

NametagGlobals.setMe(base.cam)
NametagGlobals.setCardModel('phase_3/models/props/panel.bam')
NametagGlobals.setArrowModel('phase_3/models/props/arrow.bam')
NametagGlobals.setChatBalloon3dModel('phase_3/models/props/chatbox.bam')
NametagGlobals.setChatBalloon2dModel('phase_3/models/props/chatbox_noarrow.bam')
NametagGlobals.setThoughtBalloonModel('phase_3/models/props/chatbox_thought_cutout.bam')
chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui.bam')
NametagGlobals.setPageButton(chatButtonGui.find('**/Horiz_Arrow_UP'), chatButtonGui.find('**/Horiz_Arrow_DN'),
                             chatButtonGui.find('**/Horiz_Arrow_Rllvr'), chatButtonGui.find('**/Horiz_Arrow_UP'))
NametagGlobals.setQuitButton(chatButtonGui.find('**/CloseBtn_UP'), chatButtonGui.find('**/CloseBtn_DN'),
                             chatButtonGui.find('**/CloseBtn_Rllvr'), chatButtonGui.find('**/CloseBtn_UP'))
soundRlvr = DirectGuiGlobals.getDefaultRolloverSound()
NametagGlobals.setRolloverSound(soundRlvr)
soundClick = DirectGuiGlobals.getDefaultClickSound()
NametagGlobals.setClickSound(soundClick)

from src.coginvasion.base import MusicCache
print "Precaching music..."
MusicCache.precacheMusic()

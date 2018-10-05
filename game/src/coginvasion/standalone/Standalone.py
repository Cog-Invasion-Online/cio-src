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
import __builtin__

from src.coginvasion.base.Metadata import Metadata
__builtin__.metadata = Metadata()
metadata.USE_LIGHTING = 0

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
base = CIBase()
render.setAntialias(AntialiasAttrib.MMultisample)
render.show()

if metadata.USE_LIGHTING:
    render.setShaderAuto()
else:
    render.clearShader()

from direct.distributed.ClientRepository import ClientRepository
base.cr = ClientRepository(['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
base.cr.isShowingPlayerIds = None

def isChristmas():
    return 0

base.cr.isChristmas = isChristmas

from src.coginvasion.base.CIAudio3DManager import CIAudio3DManager
base.audio3d = CIAudio3DManager(base.sfxManagerList[0], camera)
base.audio3d.setDistanceFactor(25)
base.audio3d.setDropOffFactor(0.025)

from src.coginvasion.nametag import NametagGlobals
from direct.gui import DirectGuiGlobals

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

from src.coginvasion.manager.SettingsManager import SettingsManager
jsonfile = "settings.json"
sm = SettingsManager()
from src.coginvasion.globals import CIGlobals
CIGlobals.SettingsMgr = sm
sm.loadFile(jsonfile)
sm.applyPreSettings()

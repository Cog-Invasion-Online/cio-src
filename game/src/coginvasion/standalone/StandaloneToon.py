"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file StandaloneToon.py
@author Brian Lach
@date May 02, 2015

"""

from panda3d.core import *
loadPrcFile('config/Confauto.prc')
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 2048')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'egg-load-old-curves 0')
loadPrcFileData('', 'textures-power-2 none')
loadPrcFileData('', 'load-display pandagl')
loadPrcFileData('', 'egg-flatten 0')
loadPrcFileData('', 'window-title Panda')
#loadPrcFileData('', 'fullscreen #t')
#loadPrcFileData('', 'win-size 1920 1080')

import __builtin__
from src.coginvasion.base.Metadata import Metadata
__builtin__.metadata = Metadata()

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

from src.coginvasion.manager.SettingsManager import SettingsManager

sm = SettingsManager()
sm.loadFile("settings.json")

sm.maybeFixAA()

from src.coginvasion.base.CIBase import CIBase
base = CIBase()
base.loader.mountMultifiles(None)

sm.applySettings()
from src.coginvasion.globals import CIGlobals
CIGlobals.SettingsMgr = sm
from src.coginvasion.base.CIAudio3DManager import CIAudio3DManager
base.audio3d = CIAudio3DManager(base.sfxManagerList[0], camera)
base.audio3d.setDistanceFactor(25)
base.audio3d.setDropOffFactor(0.025)
from direct.distributed.ClientRepository import ClientRepository

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

from src.coginvasion.toon import LocalToon
from src.coginvasion.login.AvChoice import AvChoice

base.shadowTrav = CollisionTraverser()
base.cr = ClientRepository(['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
base.cr.isShowingPlayerIds = False

def isChristmas():
    return False
base.cr.isChristmas = isChristmas

base.minigame = None
base.cr.localAvChoice = AvChoice("00/01/05/19/01/19/01/19/13/05/27/27/00", "Dog", 0, 0, 0)#"00/08/00/10/01/12/01/10/13/05/27/27/00", "Ducky", 0, 0)
base.musicManager.setVolume(0.65)

if False:
    dclass = base.cr.dclassesByName['DistributedPlayerToon']
    base.localAvatar = LocalToon.LocalToon(base.cr)
    base.localAvatar.dclass = dclass
    base.localAvatar.doId = base.cr.localAvChoice.getAvId()
    base.localAvatar.maxHealth = 50
    base.localAvatar.health = 50
    base.localAvatar.generate()
    base.localAvatar.setName(base.cr.localAvChoice.getName())
    base.localAvatar.setDNAStrand(base.cr.localAvChoice.getDNA())
    base.localAvatar.setBackpackAmmo("")
    base.localAvatar.announceGenerate()
    base.localAvatar.reparentTo(base.render)
    base.localAvatar.enableAvatarControls()

    if base.localAvatar.GTAControls:
        from src.coginvasion.toon.TPMouseMovement import TPMouseMovement
        mov = TPMouseMovement()
        mov.initialize()

render.setAntialias(AntialiasAttrib.MMultisample)

if metadata.USE_LIGHTING:
    #render.setAttrib(LightRampAttrib.makeHdr0())
    render.setShaderAuto()

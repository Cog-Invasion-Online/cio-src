# Filename: StandaloneToon.py
# Created by:  blach (02May15)

from panda3d.core import *
loadPrcFile('config/Confauto.prc')
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'model-path ../../../')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 2048')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'egg-load-old-curves 0')
loadPrcFileData('', 'textures-power-2 none')
loadPrcFileData('', 'load-display pandagl')
#loadPrcFileData('', 'fullscreen #t')
#loadPrcFileData('', 'win-size 1920 1080')

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

from direct.showbase.ShowBase import ShowBase
base = ShowBase()
from direct.showbase.Audio3DManager import Audio3DManager
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
base.audio3d.setDistanceFactor(25)
base.audio3d.setDropOffFactor(0.025)
from direct.distributed.ClientRepository import ClientRepository

from lib.coginvasion.nametag import NametagGlobals
from lib.coginvasion.margins.MarginManager import MarginManager
from lib.coginvasion.margins import MarginGlobals
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

base.marginManager = MarginManager()
base.margins = aspect2d.attachNewNode(base.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
base.leftCells = [
    base.marginManager.addCell(0.1, -0.6, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.0, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.4, base.a2dTopLeft)
]
base.bottomCells = [
    base.marginManager.addCell(0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-1.0, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(1.0, 0.1, base.a2dBottomCenter)
]
base.rightCells = [
    base.marginManager.addCell(-0.1, -0.6, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.0, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.4, base.a2dTopRight)
]

# HACK: I don't feel like making a new file that inherits from ShowBase so I'm just going to do this...
def setCellsActive(cells, active):
    for cell in cells:
        cell.setActive(active)
    base.marginManager.reorganize()
base.setCellsActive = setCellsActive

def windowEvent(win):
    ShowBase.windowEvent(base, win)
    base.marginManager.updateMarginVisibles()
base.windowEvent = windowEvent

base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
base.mouseWatcherNode.setButtonUpPattern('button-up-%r')

import __builtin__
class game:
	process = 'client'
__builtin__.game = game()

from lib.coginvasion.toon import LocalToon
from lib.coginvasion.login.AvChoice import AvChoice

base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()
base.lifter = CollisionHandlerFloor()
base.pusher = CollisionHandlerPusher()
base.queue = CollisionHandlerQueue()
base.cr = ClientRepository(['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
base.cr.isShowingPlayerIds = False
base.minigame = None
base.cr.localAvChoice = AvChoice("00/08/00/10/01/12/01/10/18/18/07/00/00/00/00", "Ducky", 0, 0)
base.musicManager.setVolume(0.65)

dclass = base.cr.dclassesByName['DistributedToon']
base.localAvatar = LocalToon.LocalToon(base.cr)
base.localAvatar.dclass = dclass
base.localAvatar.doId = base.cr.localAvChoice.getAvId()
base.localAvatar.generate()
base.localAvatar.setName(base.cr.localAvChoice.getName())
base.localAvatar.maxHealth = 137
base.localAvatar.health = 137
base.localAvatar.setDNAStrand(base.cr.localAvChoice.getDNA())
base.localAvatar.announceGenerate()
base.localAvatar.reparentTo(base.render)
base.localAvatar.enableAvatarControls()

base.enableParticles()

render.setAntialias(AntialiasAttrib.MMultisample)

from pandac.PandaModules import *
loadPrcFile('config/Confauto.prc')
loadPrcFile('config/config_client.prc')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.distributed.ClientRepository import ClientRepository
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
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

import __builtin__

class game:
	process = 'client'
__builtin__.game = game

#from lib.toontown.makeatoon.MakeAToon import MakeAToon
#from lib.toontown.toon.Toon import Toon

base.cr = ClientRepository(['astron/direct.dc'])
base.cr.isShowingPlayerIds = False
base.cTrav = CollisionTraverser()

base.camLens.setMinFov(70.0 / (4./3.))

DGG.setDefaultRolloverSound(base.loadSfx('phase_3/audio/sfx/GUI_rollover.mp3'))
DGG.setDefaultClickSound(base.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.mp3'))
DGG.setDefaultFont(loader.loadFont('phase_3/models/fonts/ImpressBT.ttf'))

def make_light(btn, foo):
    btn['text_fg'] = (1, 1, 1, 1)
    
def make_dark(btn, foo):
    btn['text_fg'] = (0.8, 0.8, 0.8, 1)

def make_button(text, pos, parent, command = None):
    btn = DirectButton(text = text, relief = None, scale = 0.15, pressEffect = 0,
                       text_fg = (1, 1, 1, 1), text_shadow = (0, 0, 0, 1), pos = pos,
                       text_align = TextNode.ACenter, parent = parent, command = command)
    btn.bind(DGG.ENTER, make_dark, [btn])
    btn.bind(DGG.EXIT, make_light, [btn])

from direct.actor.Actor import Actor

base.transitions.fadeScreen(0.5)

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

menuFrame = DirectFrame(scale = 0.5, pos = (0, 0, 0.3))
menuFrame.setBin('gui-popup', 60)

logo = loader.loadTexture("phase_3/maps/CogInvasion_Logo.png")
logoNode = menuFrame.attachNewNode('logoNode')
logoNode.setPos(0, 0.3, 0)
logoImg = OnscreenImage(image = logo, scale = (0.685, 0, 0.3), parent = logoNode)
logoImg.setTransparency(True)

make_button('Resume Game', (0, 0, -0.5), menuFrame)

#legs.place()

base.oobe()
base.run()

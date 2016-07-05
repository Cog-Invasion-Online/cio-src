from pandac.PandaModules import *
loadPrcFile('/c/Users/Brian/Documents/panda3d/Panda3D-CI/etc/Config.prc')
loadPrcFileData('', 'default-model-extension .egg')
from direct.showbase.ShowBase import ShowBase
base = ShowBase()
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.suit import Suit
base.enableParticles()
from lib.coginvasion.suit.CogStation import CogStation
from lib.coginvasion.dna.DNAParser import *
import __builtin__
class game:
	process = 'client'
__builtin__.game = game()
from lib.coginvasion.toon import ParticleLoader, Toon
from lib.coginvasion.hood.DistributedGagShop import DistributedGagShop
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from lib.coginvasion.globals import CIGlobals

base.cr = ClientRepository(['astron/direct.dc'])
base.cr.isShowingPlayerIds = False
base.cTrav = CollisionTraverser()

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


toon = Toon.Toon(base.cr)
toon.setDNAStrand("00/00/00/00/00/00/02/00/00/00/00/00/00/00/00")
toon.generateToon()
toon.reparentTo(render)
toon.setColorScale(0.75, 0.75, 1.0, 1.0)

print toon.getHeight()

ice = loader.loadModel('phase_8/models/props/icecube.bam')
for node in ice.findAllMatches('**/billboard*'):
	node.removeNode()
for node in ice.findAllMatches('**/drop_shadow*'):
	node.removeNode()
for node in ice.findAllMatches('**/prop_mailboxcollisions*'):
	node.removeNode()
ice.setScale(1.2, 1, toon.getHeight() / 1.7)
ice.setColor(0.76, 0.76, 1.0, 1.0)
ice.ls()

frame = DirectFrame(pos = (0, 0, 0.7))
bar = DirectWaitBar(frameColor = (1, 1, 1, 1), range = 100, value = 25, scale = (0.4, 0.5, 0.25), parent = frame, barColor = (0.55, 0.7, 1.0, 1.0))
lbl = OnscreenText(text = "SHAKE MOUSE", shadow = (0, 0, 0, 1), font = CIGlobals.getToonFont(), fg = (0.55, 0.7, 1.0, 1.0), pos = (0, -0.1, 0), parent = frame)
#mouse = OnscreenImage(image = '/c/Users/Brian/Desktop/mouse.png', scale = (0.15, 0.5, 0.3))
#mouse.setTransparency(1)

#ival = Sequence(
#	LerpPosInterval(
#		mouse,
#		duration = 0.5,
#		pos = (0.5, 0, 0),
#		startPos = (-0.5, 0, 0)
#	),
#	LerpPosInterval(
#		mouse,
#		duration = 0.5,
#		pos = (-0.5, 0, 0),
#		startPos = (0.5, 0, 0)
#	)
#)
#ival.loop()

render.setShaderAuto()

base.run()

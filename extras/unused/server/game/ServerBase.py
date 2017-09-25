from lib.server.game.ServerGlobals import *
from pandac.PandaModules import VirtualFileSystem, Filename
from direct.distributed.ServerRepository import ServerRepository
from lib.server.game.AIRepository import AIRepository
from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from direct.gui import DirectGuiGlobals
import ServerGui
notify = DirectNotify().newCategory("ServerBase")

KICK_DOID = 0x0000f

#base.disableMouse()

base.enableParticles()

render.show()

vfs = VirtualFileSystem.getGlobalPtr()
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

DirectGuiGlobals.setDefaultRolloverSound(base.loadSfx("phase_5/audio/sfx/GUI_battlerollover.ogg"))
DirectGuiGlobals.setDefaultClickSound(base.loadSfx("phase_5/audio/sfx/GUI_battleselect.ogg"))

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

port = base.config.GetInt('server-port')

ADMIN_ACCESS = 28001

class ServerBase(DirectObject):
	
	def __init__(self):
		base.sr = ServerRepository(tcpPort=port, udpPort=port, dcFileNames=['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
		base.air = AIRepository()
		base.sb = self
		self.sg = ServerGui.ServerGui()
		base.accept("escape", self.shutdownServer)
		base.accept("newConnection", self.handleNewConnection)
		base.accept("disconnection", self.handleDisconnection)
		notify.info("Server is now running")
		
	def handleNewConnection(self):
		self.sg.newConnection()
		
	def handleDisconnection(self):
		self.sg.disconnection()
		
	def sendKickMessage(self, textEntered):
		pkg = PyDatagram()
		pkg.addUint16(KICK_DOID)
		pkg.addString(textEntered)
		base.sr.sendDatagram(pkg)
		
	def sendGrantMessage(self, textEntered):
		pkg = PyDatagram()
		pkg.addUint16(ADMIN_ACCESS)
		pkg.addString(textEntered)
		base.sr.sendDatagram(pkg)
		
	def shutdownServer(self):
		base.sr.shutdownServer()
		sys.exit()
		

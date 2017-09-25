########################################
# Filename: AdminPage.py
# Created by: blach (13Apr15)
########################################

from direct.fsm.StateData import StateData
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.gui.DirectGui import *
from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals

class AdminPage(StateData):
	notify = directNotify.newCategory("AdminPage")

	def __init__(self, book, parentFSM):
		self.book = book
		self.parentFSM = parentFSM
		StateData.__init__(self, 'adminPageDone')
		self.fsm = ClassicFSM('AdminPage', [State('off', self.enterOff, self.exitOff),
			State('basePage', self.enterBasePage, self.exitBasePage),
			State('kickSection', self.enterKickSection, self.exitKickSection),
			State('sysMsgSection', self.enterSysMsgSection, self.exitSysMsgSection)],
			'off', 'off')
		self.fsm.enterInitialState()
		self.parentFSM.getStateNamed('adminPage').addChild(self.fsm)

	def enterOff(self):
		pass

	def exitOff(self):
		pass

	def enter(self):
		StateData.enter(self)
		self.fsm.request('basePage')

	def exit(self):
		self.fsm.requestFinalState()
		StateData.exit(self)

	def unload(self):
		del self.book
		del self.parentFSM
		del self.fsm
		StateData.unload(self)

	def enterSysMsgSection(self):
		self.book.createPageButtons(None, None)
		self.book.setTitle("System Message")
		geom = CIGlobals.getDefaultBtnGeom()
		self.infoLbl = OnscreenText(text = "Inform all online players about something.", pos = (0, 0.45))
		self.msgEntry = DirectEntry(
			initialText = "System Message...",
			scale = 0.055,
			width = 15,
			numLines = 4,
			command = self.sendSystemMessageCommand,
			focusInCommand = base.localAvatar.chatInput.disableKeyboardShortcuts,
			focusOutCommand = base.localAvatar.chatInput.enableKeyboardShortcuts,
			pos = (-0.4, 0, 0)

		)
		self.sendBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Send",
			pos = (0, 0, -0.35),
			text_pos = (0, -0.01),
			command = self.sendSystemMessageCommand,
		)
		self.cancelBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Cancel",
			pos = (-0.45, 0.15, -0.55),
			text_pos = (0, -0.01),
			command = self.fsm.request,
			extraArgs = ['basePage']
		)

	def sendSystemMessageCommand(self, foo = None):
		msg = self.msgEntry.get()
		base.cr.myDistrict.sendUpdate('systemMessageCommand', [base.localAvatar.getAdminToken(), msg])
		self.fsm.request('basePage')

	def exitSysMsgSection(self):
		self.infoLbl.destroy()
		del self.infoLbl
		self.msgEntry.destroy()
		del self.msgEntry
		self.sendBtn.destroy()
		del self.sendBtn
		self.cancelBtn.destroy()
		del self.cancelBtn
		self.book.clearTitle()
		self.book.deletePageButtons(False, False)

	def enterKickSection(self):
		self.book.createPageButtons(None, None)
		self.book.setTitle("Kick Player")
		geom = CIGlobals.getDefaultBtnGeom()
		self.infoLbl = OnscreenText(text = "Type the ID of the player you want to boot out.", pos = (0, 0.45))
		self.idEntry = DirectEntry(width=10, scale=0.12, pos=(-0.59, 0, 0.15), command=self.sendKickMessage,
			focusInCommand = base.localAvatar.chatInput.disableKeyboardShortcuts,
			focusOutCommand = base.localAvatar.chatInput.enableKeyboardShortcuts)
		self.kickBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Kick",
			pos = (0, 0, -0.15),
			text_pos = (0, -0.01),
			command = self.sendKickMessage,
		)
		self.banBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Ban",
			pos = (0, 0, -0.25),
			text_pos = (0, -0.01),
			command = self.sendKickMessage,
			extraArgs = [None, 1]
		)
		self.cancelBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Cancel",
			pos = (-0.45, 0.15, -0.45),
			text_pos = (0, -0.01),
			command = self.fsm.request,
			extraArgs = ['basePage']
		)

	def sendKickMessage(self, foo = None, andBan = 0):
		if self.idEntry.get().isspace() or len(self.idEntry.get()) == 0:
			return
		print "Sending out kick request for avatar id: " + str(self.idEntry.get())
		base.localAvatar.sendUpdate("requestEject", [int(self.idEntry.get()), andBan])
		self.fsm.request('basePage')

	def exitKickSection(self):
		self.banBtn.destroy()
		del self.banBtn
		self.infoLbl.destroy()
		del self.infoLbl
		self.cancelBtn.destroy()
		del self.cancelBtn
		self.idEntry.destroy()
		del self.idEntry
		self.kickBtn.destroy()
		del self.kickBtn
		self.book.deletePageButtons(False, False)
		self.book.clearTitle()

	def enterBasePage(self):
		self.book.createPageButtons('mapPage', None)
		self.book.setTitle('Admin Stuff')
		geom = CIGlobals.getDefaultBtnGeom()
		self.suitSpawnerBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "",
			pos=(-0.45, 0.15, 0.5),
			text_pos = (0, -0.01),
			command = self.sendSuitCommand,
			extraArgs = ['suitSpawner']
		)
		self.killCogsBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Kill All Cogs",
			pos=(-0.45, 0.15, 0.40),
			text_pos = (0, -0.01),
			command = self.sendSuitCommand,
			extraArgs = ['killCogs']
		)
		self.makeTournamentBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Make Cog Tournament",
			pos=(-0.45, 0.15, 0.3),
			text_pos = (0, -0.01),
			command = self.sendSuitCommand,
			extraArgs = ['tournament']
		)
		self.makeInvasionBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Make Cog Invasion",
			pos=(-0.45, 0.15, 0.2),
			text_pos = (0, -0.01),
			command = self.sendSuitCommand,
			extraArgs = ['invasion']
		)
		self.makeCogBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Make Cog",
			pos=(-0.45, 0.15, 0.1),
			text_pos = (0, -0.01),
			command = self.sendSuitCommand,
			extraArgs = ['suit']
		)
		self.ghostBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "",
			pos = (0.45, 0.15, 0.5),
			text_pos = (0, -0.01),
			command = self.changeGhost
		)
		self.bgBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Toggle Background",
			pos = (0.45, 0.15, 0.4),
			text_pos = (0, -0.01),
			command = self.toggleBackground
		)
		self.idBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Toggle Player Ids",
			pos = (0.45, 0.15, 0.3),
			text_pos = (0, -0.01),
			command = self.togglePlayerIds
		)
		self.kickBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Kick Player",
			pos = (0.45, 0.15, 0.2),
			text_pos = (0, -0.01),
			command = self.openKickPage
		)
		self.systemMsgBtn = DirectButton(
			geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "System Message",
			pos = (0.45, 0.15, 0.1),
			text_pos = (0, -0.01),
			command = self.openSysMsgPage
		)
		if base.localAvatar.getGhost():
			self.ghostBtn['text'] = 'Turn Ghost Off'
		else:
			self.ghostBtn['text'] = 'Turn Ghost On'
		base.cr.playGame.getPlace().maybeUpdateAdminPage()
		del geom

	def togglePlayerIds(self):
		if base.cr.isShowingPlayerIds:
			base.cr.hidePlayerIds()
		else:
			base.cr.showPlayerIds()

	def toggleBackground(self):
		if render.isHidden():
			render.show()
		else:
			render.hide()
		if self.book.book_img.isHidden():
			self.book.book_img.show()
		else:
			self.book.book_img.hide()

	def changeGhost(self):
		if base.localAvatar.getGhost():
			base.localAvatar.b_setGhost(0)
			self.ghostBtn['text'] = 'Turn Ghost On'
		else:
			base.localAvatar.b_setGhost(1)
			self.ghostBtn['text'] = 'Turn Ghost Off'

	def sendSuitCommand(self, commandName):
		if base.cr.playGame.suitManager:
			base.cr.playGame.suitManager.sendUpdate('suitAdminCommand', [base.localAvatar.getAdminToken(), commandName])

	def openKickPage(self):
		self.fsm.request('kickSection')

	def openSysMsgPage(self):
		self.fsm.request('sysMsgSection')

	def exitBasePage(self):
		self.systemMsgBtn.destroy()
		del self.systemMsgBtn
		self.idBtn.destroy()
		del self.idBtn
		self.kickBtn.destroy()
		del self.kickBtn
		self.bgBtn.destroy()
		del self.bgBtn
		self.ghostBtn.destroy()
		del self.ghostBtn
		self.suitSpawnerBtn.destroy()
		del self.suitSpawnerBtn
		self.killCogsBtn.destroy()
		del self.killCogsBtn
		self.makeTournamentBtn.destroy()
		del self.makeTournamentBtn
		self.makeInvasionBtn.destroy()
		del self.makeInvasionBtn
		self.makeCogBtn.destroy()
		del self.makeCogBtn
		self.book.clearTitle()
		self.book.deletePageButtons(True, False)

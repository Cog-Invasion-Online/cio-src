# Filename: DistributedPieTurretManager.py
# Created by:  blach (14Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DirectWaitBar, OnscreenImage

from lib.coginvasion.globals import CIGlobals

class DistributedPieTurretManager(DistributedObject):
	notify = directNotify.newCategory("DistributedPieTurretManager")

	def __init__(self, cr):
		try:
			self.DistributedPieTurretManager_initialized
			return
		except:
			self.DistributedPieTurretManager_initialized = 1
		DistributedObject.__init__(self, cr)
		self.myTurret = None
		self.guiFrame = None
		self.guiLabel = None
		self.guiBar = None
		self.guiBg = None

	def __pollTurret(self, turretId, task):
		turret = self.cr.doId2do.get(turretId)
		if turret != None:
			self.myTurret = turret
			self.makeGui()
			return task.done
		return task.cont

	def d_requestPlace(self, poshpr):
		self.sendUpdate("requestPlace", [poshpr])

	def turretPlaced(self, turretId):
		# We have to make sure that the turret is in self.cr.doId2do
		# before getting a handle to it and doing stuff with it or
		# else the game will crash.
		base.taskMgr.add(self.__pollTurret, 'DPTM.pollTurret', extraArgs = [turretId], appendTask = True)

	def yourTurretIsDead(self):
		base.taskMgr.remove('DPTM.pollTurret')
		self.destroyGui()
		self.myTurret = None
		if base.localAvatar.getPUInventory()[0] > 0:
			self.createTurretButton()

	def makeGui(self):
		self.destroyGui()
		self.guiFrame = DirectFrame(parent = base.a2dBottomRight, pos=(-0.55, 0, 0.15))
		self.guiBg = OnscreenImage(image = "phase_4/maps/turret_gui_bg.png", scale = (0.15, 0, 0.075), parent = self.guiFrame)
		self.guiBg.setTransparency(True)
		self.guiLabel = DirectLabel(text = "Turret", text_fg = (1, 0, 0, 1), relief = None, text_scale = 0.05, text_font = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf"), pos = (0, 0, 0.025), parent = self.guiFrame)
		self.guiBar = DirectWaitBar(range = self.myTurret.getMaxHealth(), value = self.myTurret.getHealth(), scale = 0.125, parent = self.guiFrame, pos = (0, 0, -0.01))

	def updateTurretGui(self):
		if self.guiBar:
			self.guiBar.update(self.myTurret.getHealth())

	def destroyGui(self):
		if self.guiBar:
			self.guiBar.destroy()
			self.guiBar = None
		if self.guiLabel:
			self.guiLabel.destroy()
			self.guiLabel = None
		if self.guiBg:
			self.guiBg.destroy()
			self.guiBg = None
		if self.guiFrame:
			self.guiFrame.destroy()
			self.guiFrame = None

	def createTurretButton(self):
		self.makeTurretBtn = DirectButton(
			relief = None,
			geom = CIGlobals.getDefaultBtnGeom(),
			text = "Turret",
			text_scale = 0.055,
			command = self.handleMakeTurretBtn,
			pos = (-0.47, 0, 0.1),
			geom_scale = (0.5, 1.0, 1.0),
			text_pos = (0, -0.01),
			parent = base.a2dBottomRight
		)

	def handleMakeTurretBtn(self):
		self.makeTurretBtn.destroy()
		del self.makeTurretBtn
		x, y, z = base.localAvatar.getPos()
		h, p, r = base.localAvatar.getHpr()
		self.d_requestPlace([x, y, z, h, p, r])
		base.localAvatar.sendUpdate('usedPU', [0])

	def __pollMyBattle(self, task):
		if base.localAvatar.getMyBattle():
			base.localAvatar.getMyBattle().setTurretManager(self)
			if base.localAvatar.getPUInventory()[0] > 0:
				self.createTurretButton()
			return task.done
		return task.cont

	def announceGenerate(self):
		DistributedObject.announceGenerate(self)
		taskMgr.add(self.__pollMyBattle, "__pollMyBattle")

	def disable(self):
		base.taskMgr.remove("DPTM.pollTurret")
		base.taskMgr.remove("__pollMyBattle")
		if hasattr(self, 'makeTurretBtn'):
			self.makeTurretBtn.destroy()
			del self.makeTurretBtn
		self.destroyGui()
		self.myTurret = None
		if base.localAvatar.getMyBattle():
			base.localAvatar.getMyBattle().setTurretManager(None)
		DistributedObject.disable(self)

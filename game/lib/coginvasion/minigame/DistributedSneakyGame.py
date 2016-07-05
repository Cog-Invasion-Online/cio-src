"""

  Filename: DistributedSneakyGame.py
  Created by: blach (26Oct14)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.minigame import DistributedMinigame
from lib.coginvasion.minigame.ToonFPS import ToonFPS
from direct.fsm.State import State
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from lib.coginvasion.globals import CIGlobals
from direct.distributed.ClockDelta import globalClockDelta
from RemoteToonBattleAvatar import RemoteToonBattleAvatar
import random

class DistributedSneakyGame(DistributedMinigame.DistributedMinigame):
	notify = directNotify.newCategory("DistributedSneakyGame")
	AreaModels = ["phase_11/models/lawbotHQ/LB_Zone03a.bam",
				"phase_11/models/lawbotHQ/LB_Zone04a.bam",
				"phase_11/models/lawbotHQ/LB_Zone7av2.bam",
				"phase_11/models/lawbotHQ/LB_Zone08a.bam",
				"phase_11/models/lawbotHQ/LB_Zone13a.bam",
				"phase_10/models/cashbotHQ/ZONE17a.bam",
				"phase_10/models/cashbotHQ/ZONE18a.bam",
				"phase_11/models/lawbotHQ/LB_Zone22a.bam"]
	AreaModelParents = [render, "EXIT", "EXIT", "EXIT",
					"ENTRANCE", "ENTRANCE", "ENTRANCE", "EXIT"]
	AreaModelPos = [Point3(0.00, 0.00, 0.00),
					Point3(-1.02, 59.73, 0.00),
					Point3(0.00, 74.77, 0.00),
					Point3(0.00, 89.37, -13.50),
					Point3(16.33, -136.53, 0.00),
					Point3(-1.01, -104.40, 0.00),
					Point3(0.65, -23.86, 0.00),
					Point3(-55.66, -29.01, 0.00)]
	AreaModelHpr = [Vec3(0.00, 0.00, 0.00),
				Vec3(0.00, 0.00, 0.00),
				Vec3(90.00, 0.00, 0.00),
				Vec3(180.00, 0.00, 0.00),
				Vec3(97.00, 0.00, 0.00),
				Vec3(359.95, 0.00, 0.00),
				Vec3(90.00, 0.00, 0.00),
				Vec3(270.00, 0.00, 0.00)]

	def __init__(self, cr):
		try:
			self.DistributedSneakyGame_initialized
			return
		except:
			self.DistributedSneakyGame_initialized = 1
		DistributedMinigame.DistributedMinigame.__init__(self, cr)
		self.fsm.addState(State('countdown', self.enterCountdown, self.exitCountdown, ['play']))
		self.fsm.addState(State('announceGameOver', self.enterAnnounceGameOver, self.exitAnnounceGameOver, ['finalScores']))
		self.fsm.addState(State('finalScores', self.enterFinalScores, self.exitFinalScores, ['gameOver']))
		self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
		self.fsm.getStateNamed('play').addTransition('announceGameOver')
		self.toonFps = ToonFPS(self)
		self.track = None
		self.remoteAvatars = []
		self.areas = []
		self.areaName2areaModel = {}
		self.spawnPoints = []
		self.myRemoteAvatar = None
		self.isTimeUp = False
		return

	def finalScores(self, avIdList, scoreList):
		self.toonFps.gui.handleFinalScores(avIdList, scoreList)

	def pickSpawnPoint(self):
		return random.choice(self.spawnPoints)

	def standingAvatar(self, avId):
		av = self.getRemoteAvatar(avId)
		if av:
			av.stand()

	def runningAvatar(self, avId):
		av = self.getRemoteAvatar(avId)
		if av:
			av.run()

	def jumpingAvatar(self, avId):
		av = self.getRemoteAvatar(avId)
		if av:
			av.jump()

	def getMyRemoteAvatar(self):
		return self.myRemoteAvatar

	def load(self):
		self.createWorld()
		pos, hpr = self.pickSpawnPoint()
		base.localAvatar.setPos(pos)
		base.localAvatar.setHpr(hpr)
		self.toonFps.load()
		self.myRemoteAvatar = RemoteToonBattleAvatar(self, self.cr, base.localAvatar.doId)
		self.setMinigameMusic("phase_4/audio/bgm/MG_CogThief.ogg")
		self.setDescription("Battle and defeat the other Toons with your water gun to gain points. " + \
							"Remember to reload your gun when you're out of ammo! " + \
							"The toon with the most points when the timer runs out gets a nice prize!")
		self.setWinnerPrize(70)
		self.setLoserPrize(15)
		DistributedMinigame.DistributedMinigame.load(self)

	def createWorld(self):
		self.deleteWorld()
		_numItems = 0
		name = None
		for item in self.AreaModels:
			name = 'SneakyArea-%s' % _numItems
			area = loader.loadModel(item)
			self.areas.append(area)
			self.areaName2areaModel[name] = area
			self.attachArea(_numItems)
			_numItems += 1
			self.notify.info("loaded and attached %s areas." % _numItems)
		self.createSpawnPoint(Point3(0, 0, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(-20, 50, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(20, 50, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(0, 120, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(0, 100, 0), Vec3(180, 0, 0))
		self.createSpawnPoint(Point3(-90, 0, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(-170, 0, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(-90, 50, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(-170, 50, 0), Vec3(0, 0, 0))
		self.createSpawnPoint(Point3(35, 250, 0), Vec3(-90, 0, 0))
		self.createSpawnPoint(Point3(0, 285, 0), Vec3(180, 0, 0))
		self.createSpawnPoint(Point3(-185, 250, 0), Vec3(90, 0, 0))

	def createSpawnPoint(self, pos, hpr):
		self.spawnPoints.append((pos, hpr))

	def attachArea(self, itemNum):
		name = 'SneakyArea-%s' % itemNum
		area = self.areaName2areaModel.get(name)
		parent = self.AreaModelParents[itemNum]
		if type(parent) == type(""):
			parent = self.areas[itemNum - 1].find('**/' + self.AreaModelParents[itemNum])
		pos = self.AreaModelPos[itemNum]
		hpr = self.AreaModelHpr[itemNum]
		area.reparentTo(parent)
		area.setPos(pos)
		area.setHpr(hpr)

	def deleteWorld(self):
		for area in self.areas:
			area.removeNode()
			del area

	def damage(self, amount, avId):
		self.toonFps.damageTaken(amount, avId)

	def incrementKills(self):
		self.toonFps.killedSomebody()

	def allPlayersReady(self):
		self.fsm.request('countdown')

	def timeUp(self):
		if not self.isTimeUp:
			self.fsm.request('announceGameOver')
			self.isTimeUp = True

	def enterAnnounceGameOver(self):
		whistleSfx = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.ogg")
		whistleSfx.play()
		del whistleSfx
		self.gameOverLbl = DirectLabel(text = "TIME'S\nUP!", relief = None, scale = 0.5, text_font = CIGlobals.getMickeyFont(), text_fg = (1, 0, 0, 1))
		self.track = Sequence(Wait(3.0), Func(self.fsm.request, 'finalScores'))
		self.track.start()

	def exitAnnounceGameOver(self):
		self.gameOverLbl.destroy()
		del self.gameOverLbl
		if self.track:
			self.track.pause()
			self.track = None

	def enterFinalScores(self):
		self.toonFps.gui.showFinalScores()
		self.sendUpdate('myFinalScore', [self.toonFps.points])

	def exitFinalScores(self):
		self.toonFps.gui.hideFinalScores()

	def enterCountdown(self):
		self.toonFps.fsm.request('alive')
		sec5 = base.loadSfx("phase_4/audio/sfx/announcer_begins_5sec.ogg")
		sec4 = base.loadSfx("phase_4/audio/sfx/announcer_begins_4sec.ogg")
		sec3 = base.loadSfx("phase_4/audio/sfx/announcer_begins_3sec.ogg")
		sec2 = base.loadSfx("phase_4/audio/sfx/announcer_begins_2sec.ogg")
		sec1 = base.loadSfx("phase_4/audio/sfx/announcer_begins_1sec.ogg")
		text = OnscreenText(text = "", scale = 0.1, pos = (0, 0.5), fg = (1, 1, 1, 1), shadow = (0,0,0,1))
		self.track = Sequence(
			Func(sec5.play),
			Func(text.setText, "5"),
			Wait(1.0),
			Func(sec4.play),
			Func(text.setText, "4"),
			Wait(1.0),
			Func(sec3.play),
			Func(text.setText, "3"),
			Wait(1.0),
			Func(sec2.play),
			Func(text.setText, "2"),
			Wait(1.0),
			Func(sec1.play),
			Func(text.setText, "1"),
			Wait(1.0),
			Func(text.destroy),
			Func(self.fsm.request, 'play')
		)
		self.track.start()
		del sec5
		del sec4
		del sec3
		del sec2
		del sec1
		del text

	def exitCountdown(self):
		if self.track:
			self.track.finish()
			self.track = None

	def enterPlay(self):
		DistributedMinigame.DistributedMinigame.enterPlay(self)
		self.toonFps.reallyStart()
		self.createTimer()
		#base.localAvatar.chatInput.disableKeyboardShortcuts()
		#base.localAvatar.attachCamera()
		#base.localAvatar.startSmartCamera()
		#base.localAvatar.enableAvatarControls()

	def exitPlay(self):
		self.deleteTimer()
		self.toonFps.end()
		#base.localAvatar.chatInput.enableKeyboardShortcuts()
		#base.localAvatar.disableAvatarControls()
		DistributedMinigame.DistributedMinigame.exitPlay(self)

	def attachGunToAvatar(self, avId):
		self.remoteAvatars.append(RemoteToonBattleAvatar(self, self.cr, avId))

	def d_gunShot(self):
		timestamp = globalClockDelta.getFrameNetworkTime()
		self.sendUpdate('gunShot', [base.localAvatar.doId, timestamp])

	def gunShot(self, avId, timestamp):
		ts = globalClockDelta.localElapsedTime(timestamp)
		av = self.getRemoteAvatar(avId)
		if av:
			av.fsm.request('shoot', [ts])

	def deadAvatar(self, avId, timestamp):
		ts = globalClockDelta.localElapsedTime(timestamp)
		av = self.getRemoteAvatar(avId)
		if av:
			av.fsm.request('die', [ts])

	def respawnAvatar(self, avId):
		av = self.getRemoteAvatar(avId)
		if av:
			av.exitDead()
			av.fsm.requestFinalState()

	def getRemoteAvatar(self, avId):
		for avatar in self.remoteAvatars:
			if avatar.avId == avId:
				return avatar
		return None

	def announceGenerate(self):
		DistributedMinigame.DistributedMinigame.announceGenerate(self)
		self.load()
		base.camLens.setMinFov(CIGlobals.SneakyGameFOV / (4./3.))

	def disable(self):
		DistributedMinigame.DistributedMinigame.disable(self)
		base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
		self.deleteWorld()
		self.areas = None
		self.areaName2areaModel = None
		self.isTimeUp = None
		self.toonFps.reallyEnd()
		self.toonFps.cleanup()
		self.toonFps = None
		self.spawnPoints = None
		self.myRemoteAvatar.cleanup()
		self.myRemoteAvatar = None
		for av in self.remoteAvatars:
			av.cleanup()
			del av
		self.remoteAvatars = None

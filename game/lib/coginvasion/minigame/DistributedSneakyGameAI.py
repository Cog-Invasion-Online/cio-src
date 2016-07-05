"""

  Filename: DistributedSneakyGame.py
  Created by: blach (26Oct14)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.minigame import DistributedMinigameAI
from direct.interval.IntervalGlobal import *

class DistributedSneakyGameAI(DistributedMinigameAI.DistributedMinigameAI):
	notify = directNotify.newCategory("DistributedSneakyGameAI")

	def __init__(self, air):
		try:
			self.DistributedSneakyGameAI_initialized
			return
		except:
			self.DistributedSneakyGameAI_initialized = 1
		DistributedMinigameAI.DistributedMinigameAI.__init__(self, air)
		self.setZeroCommand(self.timeUp)
		self.setInitialTime(305) # 5 minutes + the time it takes to countdown
		self.finalScoreAvIds = []
		self.finalScores = []
		self.winnerPrize = 70
		self.loserPrize = 15
		return

	def timeUp(self):
		self.sendUpdate('timeUp', [])
		Sequence(Wait(10.0), Func(self.d_gameOver)).start()

	def d_gameOver(self):
		winnerAvIds = []
		for avId in self.finalScoreAvIds:
			score = self.finalScores[self.finalScoreAvIds.index(avId)]
			if score == max(self.finalScores):
				winnerAvIds.append(avId)
		DistributedMinigameAI.DistributedMinigameAI.d_gameOver(self, 1, winnerAvIds)

	def allAvatarsReady(self):
		for avatar in self.avatars:
			self.sendUpdate('attachGunToAvatar', [avatar.doId])
		DistributedMinigameAI.DistributedMinigameAI.allAvatarsReady(self)
		self.startTiming()

	def avatarHitByBullet(self, avId, dmg):
		sender = self.air.getAvatarIdFromSender()
		self.sendUpdateToAvatarId(avId, "damage", [dmg, sender])

	def deadAvatar(self, avId, timestamp):
		sender = self.air.getAvatarIdFromSender()

	def dead(self, killerId):
		self.sendUpdateToAvatarId(killerId, 'incrementKills', [])

	def myFinalScore(self, score):
		avId = self.air.getAvatarIdFromSender()
		self.finalScoreAvIds.append(avId)
		self.finalScores.append(score)
		if len(self.finalScores) == self.numPlayers:
			self.sendUpdate('finalScores', [self.finalScoreAvIds, self.finalScores])

	def delete(self):
		self.stopTiming()
		DistributedMinigameAI.DistributedMinigameAI.delete(self)

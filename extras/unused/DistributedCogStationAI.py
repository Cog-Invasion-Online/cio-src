# Filename: DistributedCogStationAI.py
# Created by:  blach (11Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedCogBattleAI import DistributedCogBattleAI
from lib.coginvasion.minigame.DistributedGroupStationAI import DistributedGroupStationAI
import CogBattleGlobals

class DistributedCogStationAI(DistributedGroupStationAI):
	notify = directNotify.newCategory("DistributedCogStationAI")
	Slots = 8
	
	def __init__(self, air):
		try:
			self.DistributedCogStationAI_initialized
			return
		except:
			self.DistributedCogStationAI_initialized = 1
		DistributedGroupStationAI.__init__(self, air)
		self.hood = None

	def setHoodIndex(self, index):
		self.hood = index

	def getHoodIndex(self):
		return self.hood

	def monitorTime(self, task):
		if self.time == 0:
			self.stopTimer()
			self.createBattle()
			return task.done
		return task.cont

	def createBattle(self):
		zone = base.air.allocateZone()
		avIdArray = []
		for avatar in self.avatars:
			avIdArray.append(avatar.doId)
		battle = DistributedCogBattleAI(self.air)
		battle.generateWithRequired(zone)
		battle.setNumPlayers(len(self.avatars))
		battle.b_setHoodIndex(self.getHoodIndex())
		battle.b_setTotalCogs(CogBattleGlobals.HoodIndex2TotalCogs[self.getHoodIndex()])
		battle.b_setCogsRemaining(CogBattleGlobals.HoodIndex2TotalCogs[self.getHoodIndex()])
		battle.setAvIdArray(avIdArray)
		battle.startWatchingAvatars()
		for avatar in self.avatars:
			self.d_headOff(avatar.doId, zone, self.getHoodIndex())

	def d_headOff(self, avId, zone, index):
		self.sendUpdateToAvatarId(avId, "headOff", [zone, index])

	def announceGenerate(self):
		self.maxAvatars = self.Slots
		self.availableSlots = self.maxAvatars
		self.maximumSlots = self.maxAvatars
		self.resetAvailableSlots()

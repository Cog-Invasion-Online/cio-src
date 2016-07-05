# Filename: DistributedPieTurretAI.py
# Created by:  blach (14Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI

from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI

class DistributedPieTurretAI(DistributedAvatarAI, DistributedSmoothNodeAI):
	notify = directNotify.newCategory("DistributedPieTurretAI")
	MaximumRange = 40.0
	
	def __init__(self, air):
		DistributedAvatarAI.__init__(self, air)
		DistributedSmoothNodeAI.__init__(self, air)
		self.avatar = 0
		self.mgr = None
		
	def setManager(self, mgr):
		self.mgr = mgr
		
	def getManager(self):
		return self.mgr
	
	def setHealth(self, hp):
		DistributedAvatarAI.setHealth(self, hp)
		if hp < 1:
			self.getManager().sendUpdateToAvatarId(self.getAvatar(), "yourTurretIsDead", [])
			self.sendUpdate("die", [])
			Sequence(Wait(2.0), Func(self.getManager().killTurret, self.doId)).start()
		
	def startScanning(self, afterShoot = 0):
		if self.getHealth() > 0:
			timestamp = globalClockDelta.getFrameNetworkTime()
			self.sendUpdate("scan", [timestamp, afterShoot])
			taskMgr.add(self.__scan, self.uniqueName("DistributedPieTurretAI-scan"))
		
	def __scan(self, task):
		# Not sure why the task doesn't get removed on disable(), so I'm making it a try-except
		try:
			if self.getHealth() < 1:
				return task.done
			closestSuit = None
			suitId2range = {}
			for obj in self.air.doId2do.values():
				if obj.zoneId == self.zoneId:
					if obj.__class__.__name__ == "DistributedSuitAI":
						if obj.getHealth() > 0:
							suitId2range[obj.doId] = obj.getDistance(self)
			ranges = []
			for distance in suitId2range.values():
				ranges.append(distance)
			ranges.sort()
			for suitId in suitId2range.keys():
				distance = suitId2range[suitId]
				if distance == ranges[0]:
					if distance <= self.MaximumRange:
						closestSuit = self.air.doId2do.get(suitId)
						break
			if closestSuit != None and self.getHealth() > 0:
				self.sendUpdate("shoot", [closestSuit.doId])
				Sequence(Wait(0.5), Func(self.startScanning, 1)).start()
				return task.done
			task.delayTime = 0.5
			return task.again
		except:
			return task.done
		
	def setAvatar(self, avId):
		self.avatar = avId
		
	def d_setAvatar(self, avId):
		self.sendUpdate("setAvatar", [avId])
		
	def b_setAvatar(self, avId):
		self.d_setAvatar(avId)
		self.setAvatar(avId)
		
	def getAvatar(self):
		return self.avatar
		
	def disable(self):
		taskMgr.remove(self.uniqueName("DistributedPieTurretAI-scan"))
		self.avatar = None
		self.mgr = None
		DistributedSmoothNodeAI.disable(self)
		DistributedAvatarAI.disable(self)

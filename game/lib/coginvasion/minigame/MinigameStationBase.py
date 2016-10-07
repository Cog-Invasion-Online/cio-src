"""

  Filename: MinigameStationBase.py
  Created by: blach (04Oct14)
  
"""

from direct.showbase.DirectObject import *
from direct.distributed.PyDatagram import PyDatagram
import MinigameBase

STATION_SLOTS_OPEN = 901
STATION_HEAD_OFF = 902

class MinigameStationBase(DirectObject):
	
	def __init__(self, cr, game, lp):
		DirectObject.__init__(self)
		self.cr = cr
		self.game = game
		self.location_point = lp
		self.station = None
		
	def createStation(self):
		self.station = self.cr.createDistributedObject(className="DistributedMinigameStation", zoneId=30)
		self.station.b_setStation(self.game)
		self.station.b_setLocationPoint(self.location_point)
		self.station.initCollisions(self.cr.uniqueName("stationSensor"))
		self.accept(self.cr.uniqueName("stationSensor") + "-into", self.handleNewAvatar)
		self.accept("StationAvatarAbort", self.handleAvatarAbort)
		taskMgr.add(self.monitorAvatars, self.cr.uniqueName("monitorAvatars"))
		
	def handleAvatarAbort(self, doid):
		for avatar in self.station.avatars:
			if avatar.doId == doid:
				self.clearAvatar(avatar)
		
	def monitorAvatars(self, task):
		for avatar in self.station.avatars:
			if avatar.avatarType is None:
				self.clearAvatar(avatar)
		return task.cont
		
	def clearAvatar(self, avatar):
		self.station.avatars.remove(avatar)
		self.station.setAvailableSlots(self.station.getAvailableSlots() + 1)
		if len(self.station.avatars) == 0:
			self.stopTimer()
		else:
			self.resetTimer()
			
	def startTimer(self):
		taskMgr.doMethodLater(1, self.timerTask, self.cr.uniqueName("timerTask"))
		
	def stopTimer(self):
		taskMgr.remove(self.cr.uniqueName("timerTask"))
		self.station.b_setTimerTime(10)
		
	def resetTimer(self):
		self.stopTimer()
		self.startTimer()
		
	def timerTask(self, task):
		if self.station.getTimerTime() == 0:
			# Here, we'll create a DistributedMinigame and send all of
			# our avatars to the zone of the minigame we created.
			self.stopTimer()
			self.createMinigame()
			self.station.clearToons()
			return task.done
		self.station.b_setTimerTime(self.station.getTimerTime() - 1)
		task.delayTime = 1
		return task.again
		
	def createMinigame(self):
		minigame = MinigameBase.MinigameBase(self.cr)
		minigame.createMinigame(self.game, len(self.station.avatars), self.station.avatars)
		self.sendOffToons(self.game, minigame.zoneId)
		
	def sendOffToons(self, game, zoneid):
		for avatar in self.station.avatars:
			pkg = PyDatagram()
			pkg.addUint16(STATION_HEAD_OFF)
			pkg.addUint32(avatar.doId)
			pkg.addString(game)
			pkg.addUint16(zoneid)
			base.sr.sendDatagram(pkg)
		
	def handleNewAvatar(self, entry):
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToon":
				if val.getKey() == toonNP.getKey():
					if val.zoneId == 30:
						if self.station.getAvailableSlots() > 0 and not val in self.station.avatars:
							availableSlot = self.station.getAnAvailableSlot()
							pkg = PyDatagram()
							pkg.addUint16(STATION_SLOTS_OPEN)
							pkg.addUint8(availableSlot)
							pkg.addUint32(self.station.doId)
							pkg.addUint32(val.doId)
							base.sr.sendDatagram(pkg)
							self.gotNewAvatar(val)
		
	def gotNewAvatar(self, toon):
		self.station.setAvailableSlots(self.station.getAvailableSlots() - 1)
		self.station.appendToon(toon)
		if self.station.getAvailableSlots() == 2:
			self.startTimer()

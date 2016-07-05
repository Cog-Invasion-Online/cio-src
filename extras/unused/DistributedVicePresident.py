"""

  Filename: DistributedVicePresident.py
  Created by: blach (27Apr15)

"""

from panda3d.core import Point3
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta

from lib.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from VicePresident import VicePresident

class DistributedVicePresident(VicePresident, DistributedAvatar):
	notify = directNotify.newCategory("DistributedVicePresident")
	
	def __init__(self, cr):
		try:
			self.DistributedVicePresident_initialized
			return
		except:
			self.DistributedVicePresident_initialized = 1
		VicePresident.__init__(self)
		DistributedAvatar.__init__(self, cr)
	
	def throwGear(self, point, timestamp = None):
		if timestamp == None:
			ts = 0.0
		else:
			ts = globalClockDelta.localElapsedTime(timestamp)
		point = Point3(point[0], point[1], point[2])
		self.fsm.request('throwGear', [point, ts])
	
	def jump(self, timestamp = None):
		if timestamp == None:
			ts = 0.0
		else:
			ts = globalClockDelta.localElapsedTime(timestamp)
		self.fsm.request('jump', [ts])
	
	def spawn(self, timestamp = None):
		if timestamp == None:
			ts = 0.0
		else:
			ts = globalClockDelta.localElapsedTime(timestamp)
		self.fsm.request('emerge', [ts])
		
	def announceGenerate(self):
		DistributedAvatar.announceGenerate(self)
		self.fsm.request('neutral')
	
	def generate(self):
		DistributedAvatar.generate(self)
		VicePresident.generate(self)
	
	def disable(self):
		VicePresident.destroy(self)
		DistributedAvatar.disable(self)

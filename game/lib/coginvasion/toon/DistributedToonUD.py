"""

  Filename: DistributedToonUD.py
  Created by: blach (13Dec14)

"""

from direct.distributed.DistributedObjectUD import DistributedObjectUD

class DistributedToonUD(DistributedObjectUD):
	
	def __init__(self, air):
		try:
			self.DistributedToonUD_initialized
			return
		except:
			self.DistributedToonUD_initialized = 1
		DistributedObjectUD.__init__(self, air)
		return
		
	def setDNAStrand(self, dnaStrand):
		pass
	
	def setName(self, name):
		pass
		
	def setHealth(self, health):
		pass
		
	def setAnimState(self, anim, ts = 0):
		pass
		
	def setPlace(self, place):
		pass

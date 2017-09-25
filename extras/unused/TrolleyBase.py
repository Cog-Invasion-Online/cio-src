"""

  Filename: TrolleyBase.py
  Created by: blach (??July14)
  
"""

from lib.coginvasion.globals import CIGlobals
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject
from lib.coginvasion.distributed.DistributedTrolley import DistributedTrolley
from panda3d.core import *
from pandac.PandaModules import *

TROLLEY_FULL = 400000
TROLLEY_OPEN = 410000

notify = DirectNotify().newCategory("TrolleyBase")

class TrolleyBase:
	def __init__(self, cr):
		self.cr = cr
		
		self.distTrolley = self.cr.createDistributedObject(className="DistributedTrolley", zoneId=2)
		self.distTrolley.b_setDestination("OUT OF ORDER")
		#self.distTrolley.initCollisions()
		#base.accept("trolleySensor-into", self.handleAvatarEnter)
		
	def handleAvatarEnter(self, entry):
		notify.info("Got collision event: %s" % (entry))
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			# We'll only allow Toons to ride the trolley.
			if val.__class__.__name__ == "DistributedToon":
				# We'll only let the Toon come on the trolley
				# if all 4 spots are not taken, the trolley is
				# not leaving or the trolley is not gone.
				if self.distTrolley.getFilledSpots() == 4 or self.distTrolley.isLeaving() or self.distTrolley.isGone():
					# We need reject the request from the client to join the trolley.
					pkg = PyDatagram()
					pkg.addUint16(TROLLEY_FULL)
					base.sr.sendDatagram(pkg)
					return
				else:
					# We need to accept the request from the client to join the trolley.
					pkg = PyDatagram()
					pkg.addUint16(TROLLEY_OPEN)
					base.sr.sendDatagram(pkg)
		self.distTrolley.b_setFilledSpots(self.distTrolley.getFilledSpots() + 1)

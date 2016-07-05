"""

  Filename: GroupStation.py
  Created by: blach (06Jun15)

"""

from panda3d.core import *
from lib.coginvasion.globals import CIGlobals
from direct.gui.DirectGui import *

class GroupStation(NodePath):
	
	def __init__(self):
		NodePath.__init__(self, 'station')
		self.time = 10
		self.sign = None
		self.circles = []
		self.timer = None
		self.location_point = 0
		self.circle_scale = (5.5, 5, 5)
		self.circle_hpr = (180, -90, 0)
		self.signScale = 1.25
		self.standHerePath = "phase_13/models/station/stand_here.egg"
		self.eventSignPath = "phase_13/models/parties/eventSign.bam"
		self.circle_pos = {3: {1: (-7, 10, 0.05),
							2: (0, 10, 0.05),
							3: (7, 10, 0.05)},
						4: {1: (-10.5, 10, 0.05),
							2: (-3.5, 10, 0.05),
							3: (3.5, 10, 0.05),
							4: (10.5, 10, 0.05)},
						8: {1: (-10.5, 10, 0.05),
							2: (-3.5, 10, 0.05),
							3: (3.5, 10, 0.05),
							4: (10.5, 10, 0.05),
							5: (-10.5, 15, 0.05),
							6: (-3.5, 15, 0.05),
							7: (3.5, 15, 0.05),
							8: (10.5, 15, 0.05)}}
	
	def delete(self):
		self.sign = None
		self.circles = []
		self.time = None
		self.circle_xscale = None
		self.standHerePath = None
		self.eventSignPath = None
		self.availableSlots = None
		self.timer = None
		self.circle_pos = None
		self.locations = None
	
	def generateStation(self, numSlots):
		self.removeStation()
		self.sign = loader.loadModel(self.eventSignPath)
		self.sign.find('**/sign_flat').removeNode()
		self.sign.reparentTo(self)
		self.sign.setScale(self.signScale)
		for i in range(numSlots):
			circle = loader.loadModel(self.standHerePath)
			circle.reparentTo(self)
			circle.setScale(self.circle_scale)
			circle.setPos(self.circle_pos[numSlots][i + 1])
			circle.setHpr(self.circle_hpr)
			self.circles.append(circle)
		self.createTimer()
	
	def removeStation(self):
		if self.sign:
			self.sign.removeNode(); self.sign = None
		for circle in self.circles:
			circle.removeNode()
			self.circles.remove(circle)
		if self.timer:
			self.timer.destroy(); self.timer = None
	
	def createTimer(self):
		self.time = 10
		self.timer = DirectLabel(text=str(self.time), relief=None, text_font=CIGlobals.getMickeyFont(),
								text_scale=1.5, pos=(0, 0, 5.1), text_fg=(1, 0, 0, 1), text_decal=True,
								parent=self.sign)
		self.timer.setBillboardAxis(2)
		
	def setTimerTime(self, time):
		self.time = time
		self.timer['text'] = str(time)
		
	def getTimerTime(self):
		return self.time
	
	def setLocationPoint(self, location_point):
		self.location_point = location_point
		self.setPos(self.locations["pos"][location_point])
		self.setHpr(self.locations["hpr"][location_point])
		
	def getLocationPoint(self):
		return self.location_point

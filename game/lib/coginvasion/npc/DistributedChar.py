"""

  Filename: DistributedChar.py
  Created by: blach (??July14)
  
"""

from lib.coginvasion.npc import Char
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.actor.Actor import Actor

from direct.directnotify.DirectNotifyGlobal import directNotify

notify = directNotify.newCategory("DistributedChar")

class DistributedChar(Char.Char, DistributedSmoothNode):
	
	def __init__(self, cr):
		self.cr = cr
		Char.Char.__init__(self)
		DistributedSmoothNode.__init__(self, cr)
		self.name = ""
		self.anim = ""
		self.chat = ""
		self.charType = ""
		self.clerk = 0
		
	def initializeLocalCollisions(self, name, radius):
		Char.Char.initializeLocalCollisions(self, name, radius)
		
	def setChar(self, charType, clerk=0):
		self.charType = charType
		self.clerk = clerk
		notify.info("setting char as %s" % (charType))
		if clerk:
			self.setupGagWheelBarrel()
		Char.Char.generateChar(self, charType)
		
	def setupGagWheelBarrel(self):
		self.wb = loader.loadModel("phase_5.5/models/estate/wheelbarrel.bam")
		self.wb.find('**/dirt').remove_node()
		self.wb.reparent_to(self)
		self.wb.set_x(-3.5)
		self.wb.set_h(90)
		tart1 = loader.loadModel("phase_3.5/models/props/tart.bam")
		tart1.reparent_to(self.wb)
		tart1.set_scale(0.6)
		tart1.set_pos(0, 0.65, 1)
		tart1.set_p(30.26)
		tart2 = loader.loadModel("phase_3.5/models/props/tart.bam")
		tart2.reparent_to(self.wb)
		tart2.set_scale(0.6)
		tart2.set_z(1.14)
		slice1 = loader.loadModel("phase_5/models/props/cream-pie-slice.bam")
		slice1.reparent_to(self.wb)
		slice1.set_scale(0.6)
		slice1.set_pos(0, -0.56, 1.42)
		slice1.set_hpr(323.97, 37.87, 0)
		slice2 = loader.loadModel("phase_5/models/props/cream-pie-slice.bam")
		slice2.reparent_to(self.wb)
		slice2.set_scale(0.6)
		slice2.set_pos(tart2.get_pos() + (0, 0, 0.35))
		slice2.set_hpr(tart2.get_hpr())
		cake1 = Actor("phase_5/models/props/birthday-cake-mod.bam",
					{"chan": "phase_5/models/props/birthday-cake-chan.bam"})
		cake1.setPlayRate(0.3, "chan")
		cake1.loop("chan")
		cake1.set_scale(0.6)
		cake1.reparent_to(self.wb)
		cake1.set_pos(0, 0.94, 1.40)
		cake2 = Actor("phase_5/models/props/birthday-cake-mod.bam",
					{"chan": "phase_5/models/props/birthday-cake-chan.bam"})
		cake2.setPlayRate(-0.3, "chan")
		cake2.loop("chan")
		cake2.set_scale(0.5)
		cake2.reparent_to(self.wb)
		cake2.set_pos(0.27, -0.38, 1.7)
		cake2.set_p(10)
		
	def b_setChar(self, charType, clerk=0):
		self.d_setChar(charType, clerk)
		self.setChar(charType, clerk)
		
	def d_setChar(self, charType, clerk=0):
		self.sendUpdate("setChar", [charType, clerk])
		
	def getChar(self):
		return tuple((self.charType, self.clerk))
		
	def setName(self, name):
		self.name = name
		Char.Char.setName(self, name)
	
	def b_setName(self, name):
		self.d_setName(name)
		self.setName(name)
		
	def d_setName(self, name):
		self.sendUpdate("setName", [name])
		
	def getName(self):
		return self.name
		
	def setChat(self, chat):
		self.chat = chat
		Char.Char.setChat(self, chat)
		
	def b_setChat(self, chat):
		self.d_setChat(chat)
		self.setChat(chat)
		
	def d_setChat(self, chat):
		self.sendUpdate("setChat", [chat])
		
	def getChat(self):
		return self.chat
		
	def setAnimState(self, anim):
		self.anim = anim
		self.animFSM.request(anim)
		
	def b_setAnimState(self, anim):
		self.d_setAnimState(anim)
		self.setAnimState(anim)
	
	def d_setAnimState(self, anim):
		self.sendUpdate("setAnimState", [anim])
		
	def getAnimState(self):
		return self.anim
		
	def __showAvId(self):
		self.setDisplayName(self.getName() + "\n[" + str(self.doId) + "]")
		
	def __showName(self):
		self.setDisplayName(self.getName())
		
	def setDisplayName(self, name):
		Char.Char.setName(self, name)
		
	def announceGenerate(self):
		DistributedSmoothNode.announceGenerate(self)
		self.reparentTo(render)
		
	def generate(self):
		DistributedSmoothNode.generate(self)
		
		self.activateSmoothing(True, False)
		self.startSmooth()
		self.accept("showAvId", self.__showAvId)
		self.accept("showName", self.__showName)
		
	def disable(self):
		self.stopSmooth()
		self.ignore('showAvId')
		self.ignore('showName')
		self.detachNode()
		DistributedSmoothNode.disable(self)
		
	def delete(self):
		del self.name
		del self.charType
		del self.anim
		del self.chat
		if self.clerk:
			self.wb.remove_node()
			del self.wb
		Char.Char.delete(self)
		DistributedSmoothNode.delete(self)
		

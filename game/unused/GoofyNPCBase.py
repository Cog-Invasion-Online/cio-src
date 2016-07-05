"""

  Filename: GoofyNPCBase.py
  Created by: blach (??July14)
  
"""

from lib.coginvasion.globals import CIGlobals
from direct.gui.DirectGui import *
from direct.directnotify.DirectNotify import DirectNotify
from pandac.PandaModules import *
from panda3d.core import *
from direct.task import Task
import random
from lib.coginvasion.hood.HoodUtil import HoodUtil
from panda3d.ai import *

notify = DirectNotify().newCategory("GoofyNPCBase")

GAG_SHOP = 7000

class GoofyNPCBase:
	
	def __init__(self, cr, clerk = 1):
		self.cr = cr
		self.goofy = None
		self.inConvo = 0
		self.clerk = clerk
		self.isNeutral = False
		self.keyMap = None
		self.nearbyToons = []
		self.createReady()
	
	def createReady(self):
		notify.info("generating Char %s in %s..." % (CIGlobals.Goofy, CIGlobals.ToontownCentral))
		self.goofy = self.cr.createDistributedObject("DistributedChar", zoneId=20)
		self.collider_name = self.cr.uniqueName("goofy")
		if self.clerk:
			self.goofy.initializeLocalCollisions(self.collider_name, 5)
		else:
			self.goofy.initializeLocalCollisions(self.collider_name, 15)
		self.goofy.b_setChar(CIGlobals.Goofy, clerk=self.clerk)
		self.goofy.startPosHprBroadcast()
		self.goofy.b_setName(CIGlobals.Goofy)
		self.goofy.b_setAnimState("neutral")
		if self.clerk:
			self.initClerk()
		else:
			self.initAI()
		
		base.accept(self.collider_name + "s-into", self.avatarEnter)
		base.accept(self.collider_name + "s-out", self.avatarExit)
		base.accept("gagShopExit", self.handleGagShopExit)
		
	def initClerk(self):
		self.goofy.set_pos(self.cr.getCurrentHood().clerk_node.get_pos(render))
		self.goofy.set_h(-15)
		self.goofy.b_setAnimState("neutral")

	def initAI(self):
		self.AIWorld = AIWorld(render)
		
		self.AIGoofy = AICharacter(CIGlobals.Goofy, self.goofy, -60, 10, -5)
		self.AIWorld.addAiChar(self.AIGoofy)
		self.AIBehaviors = self.AIGoofy.getAiBehaviors()
		
		taskMgr.add(self.createPath, "createNewPath")
		taskMgr.add(self.worldUpdate, "worldUpdate")
		
	def worldUpdate(self, task):
		self.AIGoofy.setMass(self.AIGoofy.getMass() * globalClock.getDt() - 50 * CIGlobals.NPCWalkSpeed / globalClock.getDt())
		try: self.AIWorld.update()
		except: pass
		return task.cont
		
	def createPath(self, task):
		if self.inConvo == 1:
			return task.done
		self.isNeutral = False
		self.randomPath = random.randint(0, 8)
		self.AIBehaviors.pathFollow(1)
		
		if self.randomPath == 0:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['a'])
		elif self.randomPath == 1:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['b'])
		elif self.randomPath == 2:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['c'])
		elif self.randomPath == 3:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['d'])
		elif self.randomPath == 4:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['e'])
		elif self.randomPath == 5:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['f'])
		elif self.randomPath == 6:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['g'])
		elif self.randomPath == 7:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['h'])
		elif self.randomPath == 8:
			self.AIBehaviors.addToPath(CIGlobals.MickeyPaths['i'])
			
		self.startFollow()
			
	def startFollow(self):
		self.AIBehaviors.startFollow()
		self.goofy.b_setAnimState("walk")
		taskMgr.add(self.checkPathStatus, "checkPathStatus")
		
	def checkPathStatus(self, task):
		if self.AIBehaviors.behaviorStatus("pathfollow") == 'done':
			if self.inConvo == 1:
				return task.done
			self.isNeutral = True
			self.goofy.b_setAnimState("neutral")
			self.randomWait = random.randint(3, 15)
			taskMgr.doMethodLater(self.randomWait, self.createPath, "createNewPath")
			return task.done
		return task.cont
			
	def startGoofyConversation(self):
		self.inConvo = 1
		self.numMsgs = 0
		self.AIBehaviors.pauseAi('pathfollow')
		self.goofy.b_setAnimState("walk")
		self.toon = self.getToon2Talk2()
		self.currentHpr = self.goofy.getHpr()
		self.goofy.headsUp(self.toon)
		self.turnHpr = self.goofy.getHpr()
		self.goofy.setHpr(self.currentHpr)
		cchar_turnInt = self.goofy.hprInterval(0.5,
											Point3(self.turnHpr),
											startHpr=(self.currentHpr))
		cchar_turnInt.start()
		taskMgr.doMethodLater(0.5, self.goofyTalk, "goofyTalk")
		taskMgr.doMethodLater(9, self.continueGoofyConversation, "cmc")
		
	def continueGoofyConversation(self, task):
		if self.isLonely() or self.toon.avatarType is None:
			taskMgr.add(self.continuePath, "continuePath")
			return task.done
		self.goofy.headsUp(self.toon)
		taskMgr.add(self.goofyTalk, "goofyTalk")
		task.delayTime = 8.5
		return task.again
		
	def goofyTalk(self, task):
		if not self.goofy.getAnimState() == "neutral":
			self.goofy.b_setAnimState("neutral")
		if self.isNewConversation():
			chat_msg = random.randint(0, len(CIGlobals.SharedChatterGreetings) - 1)
			if chat_msg == 2:
				self.goofy.b_setChat(CIGlobals.SharedChatterGreetings[chat_msg])
			else:
				self.goofy.b_setChat(CIGlobals.SharedChatterGreetings[chat_msg] % (self.toon.getName()))
			self.numMsgs += 1
			return task.done
		if self.isReadyToLeave():
			chat_msg = random.randint(0, len(CIGlobals.SharedChatterGoodbyes) - 1)
			if chat_msg == 2 or chat_msg == 7 or chat_msg == 10:
				self.goofy.b_setChat(CIGlobals.SharedChatterGoodbyes[chat_msg] % (self.toon.getName()))
			else:
				self.goofy.b_setChat(CIGlobals.SharedChatterGoodbyes[chat_msg])
			taskMgr.doMethodLater(2, self.continuePath, "continuePath")
			self.numMsgs += 1
			return task.done
		else:
			if self.wantsUniqueChat():
				chat_msg = random.randint(0, len(CIGlobals.GoofySpeedwayChatter) - 1)
				if chat_msg == 2:
					self.goofy.b_setChat(CIGlobals.GoofySpeedwayChatter[chat_msg] % (self.toon.getName()))
				else:
					self.goofy.b_setChat(CIGlobals.GoofySpeedwayChatter[chat_msg])
			else:
				chat_msg = random.randint(0, len(CIGlobals.SharedChatterComments) - 1)
				if chat_msg == 0:
					self.goofy.b_setChat(CIGlobals.SharedChatterComments[chat_msg] % (self.toon.getName()))
				else:
					self.goofy.b_setChat(CIGlobals.SharedChatterComments[chat_msg])
		self.numMsgs += 1
		return task.done

	def continuePath(self, task):
		self.inConvo = 0
		self.clearAvatars()
		taskMgr.add(self.createPath, "createNewPath")
		self.goofy.b_setAnimState("walk")
		return task.done
		
	def avatarEnter(self, entry):
		""" An avatar has entered our collisionEvent bubble.
		Let's add the avatar to the nearby avatar list only
		if the avatar is a Toon. """
		
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			print val.__class__.__name__
			if val.__class__.__name__ == "DistributedToonAI":
				if val.getKey() == toonNP.getKey():
					if val.getPlace() == CIGlobals.ToontownCentral:
						if self.clerk:
							targetDoId = key
							self.sendGagShopEnter(targetDoId)
						else:
							self.handleNewAvatar(val)
	
	def sendGagShopEnter(self, targetDoId):
		pkg = PyDatagram()
		pkg.addUint16(GAG_SHOP)
		pkg.addUint32(targetDoId)
		base.sr.sendDatagram(pkg)
		
	def handleGagShopExit(self):
		# Say goodbye to the person who left
		# the gag shop...
		self.goofy.b_setChat(CIGlobals.GagShopGoodbye)
					
	def avatarExit(self, entry):
		""" An avatar that was in the nearby range has gone
		out of range. We need to remove the avatar from the
		nearby avatar list. """
		
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToon":
				if val.zoneId == 20:
					if not self.clerk:
						self.handleOldAvatar(val)
					
	def handleOldAvatar(self, val):
		if val in self.nearbyToons:
			self.nearbyToons.remove(val)
			
	def handleNewAvatar(self, val):
		if not val in self.nearbyToons:
			self.nearbyToons.append(val)
			if self.wantsToTalk() and self.inConvo == 0:
				self.startGoofyConversation()
		
	def clearAvatars(self):
		self.nearbyToons = []
		
	def getNearbyToons(self):
		return self.nearbyToons
		
	def getToon2Talk2(self):
		toon = random.randint(0, len(self.nearbyToons) - 1)
		return self.nearbyToons[toon]
		
	def isNewConversation(self):
		if self.numMsgs == 0:
			return True
		else:
			return False
			
	def wantsUniqueChat(self):
		chat = random.randint(0, 3)
		if chat == 3:
			return True
		else:
			return False
		
	def isReadyToLeave(self):
		if self.numMsgs >= 10:
			return True
		else:
			return False
		
	def wantsToTalk(self):
		return self.isNeutral
		
	def isLonely(self):
		if self.getNearbyToons() == []:
			return True
		else:
			return False
			
	def setKey(self, key, value):
		self.keyMap[key] = value
			
	def moveCamera(self, task):
		if self.keyMap["left"] == 1:
			camera.setH(camera, + 80 * globalClock.getDt())
		elif self.keyMap["right"] == 1:
			camera.setH(camera,  - 80 * globalClock.getDt())
		elif self.keyMap["forward"] == 1:
			if camera.getY() >= 20:
				return Task.cont
			camera.setY(camera, + 20 * globalClock.getDt())
		elif self.keyMap["back"] == 1:
			if camera.getY() <= -20:
				return Task.cont
			camera.setY(camera, - 20 * globalClock.getDt())
			
		return Task.cont

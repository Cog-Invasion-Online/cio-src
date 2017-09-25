"""
 
  Filename: MickeyNPCBase.py
  Created by: blach (??June14)
  
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

notify = DirectNotify().newCategory("MickeyNPCBase")

class MickeyNPCBase:
	
	def __init__(self, cr):
		self.cr = cr
		self.mickey = None
		
		self.inConvo = 0
		
		self.isNeutral = False
		
		self.keyMap = None
		
		self.nearbyToons = []
		
		self.createReady()
	
	def createReady(self):
		notify.info("generating Char %s in %s..." % (CIGlobals.Mickey, CIGlobals.ToontownCentral))
		self.mickey = self.cr.createDistributedObject("DistributedChar", zoneId=20)
		self.collider_name = self.cr.uniqueName("mickey")
		self.mickey.initializeLocalCollisions(self.collider_name, 15)
		self.mickey.b_setChar(CIGlobals.Mickey)
		self.mickey.startPosHprBroadcast()
		self.mickey.b_setName(CIGlobals.Mickey)
		self.initAI()
		
		self.keyMap = {"left": 0, "right": 0, "forward": 0, "back": 0}
		
		base.accept(self.collider_name + "s-into", self.avatarEnter)
		base.accept(self.collider_name + "s-out", self.avatarExit)
		
		base.accept("f3", aspect2d.hide)
		base.accept("f4", aspect2d.show)
		
	def setupCamera(self):
		camera.reparentTo(base.avatar)
		camera.setPos(0, -18, 5)
		camera.lookAt(base.avatar, 0, 0, 4)
		taskMgr.add(self.moveCamera, "moveCamera")
		
		base.accept("arrow_left", self.setKey, ["left", 1])
		base.accept("arrow_left-up", self.setKey, ["left", 0])
		base.accept("arrow_right", self.setKey, ["right", 1])
		base.accept("arrow_right-up", self.setKey, ["right", 0])
		base.accept("arrow_up", self.setKey, ["forward", 1])
		base.accept("arrow_up-up", self.setKey, ["forward", 0])
		base.accept("arrow_down", self.setKey, ["back", 1])
		base.accept("arrow_down-up", self.setKey, ["back", 0])

	def initAI(self):
		self.AIWorld = AIWorld(render)
		
		self.AIMickey = AICharacter(CIGlobals.Mickey, self.mickey, -60, 10, -5)
		self.AIWorld.addAiChar(self.AIMickey)
		self.AIBehaviors = self.AIMickey.getAiBehaviors()
		
		taskMgr.add(self.createPath, "createNewPath")
		taskMgr.add(self.worldUpdate, "worldUpdate")
		
	def worldUpdate(self, task):
		self.AIMickey.setMass(self.AIMickey.getMass() * globalClock.getDt() - 50 * CIGlobals.NPCWalkSpeed / globalClock.getDt())
		try: self.AIWorld.update()
		except: self.fixNan()
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
		self.mickey.b_setAnimState("walk")
		taskMgr.add(self.checkPathStatus, "checkPathStatus")
		
	def checkPathStatus(self, task):
		if self.AIBehaviors.behaviorStatus("pathfollow") == 'done':
			if self.inConvo == 1:
				return task.done
			self.isNeutral = True
			self.mickey.b_setAnimState("neutral")
			self.randomWait = random.randint(3, 15)
			taskMgr.doMethodLater(self.randomWait, self.createPath, "createNewPath")
			return task.done
		return task.cont
			
	def startMickeyConversation(self):
		self.inConvo = 1
		self.numMsgs = 0
		self.AIBehaviors.pauseAi('pathfollow')
		self.mickey.b_setAnimState("walk")
		self.toon = self.getToon2Talk2()
		self.currentHpr = self.mickey.getHpr()
		self.mickey.headsUp(self.toon)
		self.turnHpr = self.mickey.getHpr()
		self.mickey.setHpr(self.currentHpr)
		cchar_turnInt = self.mickey.hprInterval(0.5,
											Point3(self.turnHpr),
											startHpr=(self.currentHpr))
		cchar_turnInt.start()
		taskMgr.doMethodLater(0.5, self.mickeyTalk, "mickeyTalk")
		taskMgr.doMethodLater(9, self.continueMickeyConversation, "cmc")
		
	def continueMickeyConversation(self, task):
		if self.isLonely() or self.toon.avatarType is None:
			taskMgr.add(self.continuePath, "continuePath")
			return task.done
		self.mickey.headsUp(self.toon)
		taskMgr.add(self.mickeyTalk, "mickeyTalk")
		task.delayTime = 8.5
		return task.again
		
	def mickeyTalk(self, task):
		if not self.mickey.getAnimState() == "neutral":
			self.mickey.b_setAnimState("neutral")
		if self.isNewConversation():
			chat_msg = random.randint(0, len(CIGlobals.SharedChatterGreetings) - 1)
			if chat_msg == 2:
				self.mickey.b_setChat(CIGlobals.SharedChatterGreetings[chat_msg])
			else:
				self.mickey.b_setChat(CIGlobals.SharedChatterGreetings[chat_msg] % (self.toon.getName()))
			self.numMsgs += 1
			return task.done
		if self.isReadyToLeave():
			chat_msg = random.randint(0, len(CIGlobals.SharedChatterGoodbyes) - 1)
			if chat_msg == 2 or chat_msg == 7 or chat_msg == 10:
				self.mickey.b_setChat(CIGlobals.SharedChatterGoodbyes[chat_msg] % (self.toon.getName()))
			else:
				self.mickey.b_setChat(CIGlobals.SharedChatterGoodbyes[chat_msg])
			taskMgr.doMethodLater(2, self.continuePath, "continuePath")
			self.numMsgs += 1
			return task.done
		else:
			if self.wantsUniqueChat():
				chat_msg = random.randint(0, len(CIGlobals.MickeyChatter) - 1)
				self.mickey.b_setChat(CIGlobals.MickeyChatter[chat_msg])
			else:
				chat_msg = random.randint(0, len(CIGlobals.SharedChatterComments) - 1)
				if chat_msg == 0:
					self.mickey.b_setChat(CIGlobals.SharedChatterComments[chat_msg] % (self.toon.getName()))
				else:
					self.mickey.b_setChat(CIGlobals.SharedChatterComments[chat_msg])
		self.numMsgs += 1
		return task.done

	def continuePath(self, task):
		self.inConvo = 0
		self.clearAvatars()
		taskMgr.add(self.createPath, "createNewPath")
		self.mickey.b_setAnimState("walk")
		return task.done
		
	def fixNan(self):
		self.AIBehaviors.removeAi('pathfollow')
		taskMgr.add(self.createPath, "createPath")
		
	def avatarEnter(self, entry):
		""" An avatar has entered our collisionEvent bubble.
		Let's add the avatar to the nearby avatar list only
		if the avatar is a Toon. """
		
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToon":
				if val.getKey() == toonNP.getKey():
					if val.zoneId == 20:
						self.handleNewAvatar(val)
					
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
					self.handleOldAvatar(val)
					
	def handleOldAvatar(self, val):
		if val in self.nearbyToons:
			self.nearbyToons.remove(val)
			
	def handleNewAvatar(self, val):
		if not val in self.nearbyToons:
			self.nearbyToons.append(val)
			if self.wantsToTalk() and self.inConvo == 0:
				self.startMickeyConversation()
		
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

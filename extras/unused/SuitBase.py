"""

  Filename: SuitBase.py
  Created by: blach (??June14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.TTCHood import *
from direct.distributed.ClientRepository import ClientRepository
from direct.distributed.PyDatagram import PyDatagram
from panda3d.ai import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.directnotify.DirectNotify import DirectNotify
from direct.interval.IntervalGlobal import *
from lib.coginvasion.suit import SuitBoss
from lib.coginvasion.npc.NPCWalker import *
import random
import sys
			
notify = DirectNotify().newCategory("SuitBase")

TOON_DOID = 31000
JBS_COLLECTED = 7001

class SuitBase:
	
	def __init__(self, cr, type, head, team, skeleton):
		self.cr = cr
		
		self.type = type
		self.head = head
		self.team = team
		self.skeleton = skeleton
		self.AiBehaviors = None
		self.distSuit = None
		self.isAttacking = False
		self.nextDestination = None
		self.lastDestination = None
		self.createReady()
		
	def createReady(self):
		notify.info("generating Suit%s with head %s on team %s..." % (self.type, self.head, self.team))
		self.distSuit = self.cr.createDistributedObject(className='DistributedSuitAI', zoneId=20)
		self.distSuit.setBase(self)
		self.distSuit.b_setSuit(self.type, self.head, self.team, self.skeleton)
		if self.skeleton:
			self.distSuit.b_setName(CIGlobals.Skelesuit)
		else:
			self.distSuit.b_setName(CIGlobals.SuitNames[self.head])
		base.air.Suits.append(self)
		self.spawnSuit()
		
	def spawnSuit(self):
		self.random_landSpot = random.randint(0, len(CIGlobals.SuitPaths) - 1)
		self.distSuit.b_setAnimState('flydown')
		suitLand = self.distSuit.posInterval(3,
								CIGlobals.SuitPaths[self.random_landSpot],
								startPos=(CIGlobals.SuitPaths[self.random_landSpot] + (0, 0, 50)))
		suitLand.start()
		self.distSuit.startPosHprBroadcast()
		yaw = random.uniform(0.0, 360.0)
		self.distSuit.setH(yaw)
		taskMgr.doMethodLater(5.4, self.startSuit, "initAi")
			
	def startSuit(self, task):
		self.distSuit.b_setAnimState("neutral")
		self.startAttacks()
		if self.head == "vp":
			self.suitBoss = SuitBoss.SuitBoss(self)
			self.suitBoss.startBoss()
		else:
			self.initAi()
		taskMgr.add(self.checkHealth, "checkHealth")
		
	def initAi(self):
		self.AiWorld = AIWorld(render)
		dt = globalClock.getDt()
		self.AiSuit = AICharacter("suit", self.distSuit, -60, 10, -5)
		self.AiWorld.addAiChar(self.AiSuit)
		self.AiBehaviors = self.AiSuit.getAiBehaviors()
		
		base.accept("suitDoId", self.handleDoId)
		
		self.collider_name = self.cr.uniqueName("suit")
		self.distSuit.initializeLocalCollisions(self.collider_name)
		self.distSuit.initializeRay(self.collider_name)
		taskMgr.doMethodLater(1, self.createPath, "createPath")
		taskMgr.add(self.AiWorldUpdate, "awu")
		
	#def thinkAboutNewPath(self):
	#	if self.nextDestination == 0 or self.nextDestination == 1:
	#		possibleDests = CIGlobals.SuitPaths
	#	elif self.nextDestination == 2:
	#		possibleDests = [3, 12, 11, 9, 10, 1, 0, 24, 4, 14, 22, 15, 20, 8, 17]
		
	def startAttacks(self):
		if self.head != "vp":
			attackTime = random.randint(8, 20)
		else:
			attackTime = random.randint(8, 12)
		self.attackId = random.uniform(0, 101010101010)
		self.distSuit.attackId = self.attackId
		taskMgr.doMethodLater(attackTime, self.attackTask, "attackTask" + str(self.attackId))
		
	def AiWorldUpdate(self, task):
		if not hasattr(self, 'AiSuit'):
			return task.done
		self.AiSuit.setMass(self.AiSuit.getMass() * globalClock.getDt() - 50 * CIGlobals.NPCWalkSpeed / globalClock.getDt())
		try: self.AiWorld.update()
		except: self.fixNan()
		return task.cont
		
	def tauntTask(self, task):
		""" Will pick a random phrase out of the SuitGeneralTaunts
		list in CIGlobals and say it. """
		
		if self.distSuit.state == "dead" or self.distSuit.state == "dying":
			return task.done
		self.random_GeneralTaunt = random.randint(0, 12)
		self.distSuit.b_setChat(CIGlobals.SuitGeneralTaunts[self.random_GeneralTaunt])
		self.random_delayTime = random.randint(15, 30)
		task.delayTime = self.random_delayTime
		return task.again
		
	def createPath(self, task):
		self.randomPath = random.randint(0, len(CIGlobals.SuitPaths) - 1)
		self.AiBehaviors.pathFollow(1)
		path = CIGlobals.SuitPaths[self.randomPath]
		self.AiBehaviors.addToPath(CIGlobals.SuitPaths[self.randomPath])
		self.lastDestination = self.nextDestination
		self.nextDestination = path
			
		self.startFollow()
		return task.done
		
	def startFollow(self):
		self.AiBehaviors.startFollow()
		self.distSuit.b_setAnimState("walk")
		taskMgr.add(self.checkPathStatus, self.cr.uniqueName("checkPathStatus"))
		
	def checkPathStatus(self, task):
		if self.AiBehaviors.behaviorStatus("pathfollow") == 'done':
			taskMgr.add(self.createPath, "createPath")
			return task.done
		return task.cont
		
	def checkHealth(self, task):
		if self.distSuit.getHealth() <= 0:
			if self.AiBehaviors:
				self.AiBehaviors.removeAi("pathfollow")
			self.distSuit.b_setAnimState("pie")
			self.distSuit.d_interruptAttack()
			if self.head == "vp":
				self.suitBoss.stopBoss()
			taskMgr.doMethodLater(2, self.loserSuit, "loserSuit")
			return task.done
		return task.cont
		
	def loserSuit(self, task):
		self.distSuit.b_setAnimState("die")
		taskMgr.doMethodLater(6, self.closeSuit, "closeSuit")
		return task.done
		
	def createJellyBean(self, task):
		self.AiWorld.removeAiChar("suit")
		del self.AiSuit
		base.air.deadSuit()
		self.deleteLocalCollisions()
		self.distSuit.b_createJellyBean()
		self.initJbCollisions()
		return task.done
		
	def deleteLocalCollisions(self):
		self.distSuit.deleteLocalCollisions()
		
	def initJbCollisions(self):
		name = self.cr.uniqueName("jellybean")
		collisionSphere = CollisionSphere(0, 0, 0, 2)
		sensorNode = CollisionNode(name + "s")
		sensorNode.addSolid(collisionSphere)
		self.jsensorNodePath = self.distSuit.attachNewNode(sensorNode)
		self.jsensorNodePath.node().setFromCollideMask(CIGlobals.EventBitmask)
		self.jsensorNodePath.node().setIntoCollideMask(BitMask32.allOff())
		self.jsensorNodePath.setZ(1)
		self.jsensorNodePath.show()
		event = CollisionHandlerEvent()
		event.setInPattern("%fn-into")
		event.setOutPattern("%fn-out")
		base.cTrav.addCollider(self.jsensorNodePath, event)
		base.acceptOnce(name + "s-into", self.handleJbCollisions)
		taskMgr.doMethodLater(30, self.deleteJellybean, self.cr.uniqueName("removeBean"))
		
	def handleJbCollisions(self, entry):
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToonAI":
				print val.getKey()
				print toonNP.getKey()
				if val.getKey() == toonNP.getKey():
					if val.zoneId == 2:
						targetDoId = key
						self.sendCollectJbs(targetDoId)
						self.deleteJellybean()
						break
				
	def stopJellybean(self):
		taskMgr.remove(self.cr.uniqueName("removeBean"))
		self.deleteJellybean(None)
		
	def deleteJellybean(self, task):
		self.distSuit.b_deleteJellybean()
		self.closeSuit(None)
					
	def sendCollectJbs(self, doid):
		pkg = PyDatagram()
		money = int(self.maxHP / CIGlobals.SuitAttackDamageFactors['clipontie'])
		pkg.addUint16(money)
		pkg.addUint16(JBS_COLLECTED)
		pkg.addUint32(doid)
		base.sr.sendDatagram(pkg)
		
	def closeSuit(self, task):
		if self.head != "vp":
			self.AiWorld.removeAiChar("suit")
			del self.AiSuit
			self.deleteLocalCollisions()
		base.air.deadSuit()
		self.distSuit.sendDeleteMsg()
		base.air.Suits.remove(self)
		return task.done
		
	def handleDoId(self, doId):
		for suitId in range(base.air.SuitCount):
			if doId == base.air.Suits[suitId].doId:
				if not base.air.Suits[suitId].getHealth() <= 0:
					base.air.Suits[suitId].b_setDamage(36)
					
	def attackTask(self, task):
		if self.distSuit.avatarType == None or self.distSuit.getHealth() <= 0:
			return task.done
		if self.head == "vp":
			# We can't attack while we're flying
			if not self.suitBoss.getFlying():
				self.chooseVictim()
		else:
			self.chooseVictim()
		if self.head != "vp":
			delay = random.randint(6, 15)
		else:
			delay = random.randint(6, 12)
		task.delayTime = delay
		return task.again
		
	def suitVictory(self):
		if self.head != "vp":
			taskMgr.doMethodLater(8.5, self.continuePath, "continuePath" + str(self.continuePathId))
			self.AiBehaviors.pauseAi('pathfollow')
		taskMgr.remove("continuePath" + str(self.continuePathId))
		taskMgr.remove("attackTask" + str(self.attackId))
		self.distSuit.b_setAnimState("win")
		attackDelay = random.randint(6, 15)
		taskMgr.doMethodLater(attackDelay, self.attackTask, "attackTask" + str(self.attackId))
					
	def chooseVictim(self):
		toons = []
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToonAI" or val.__class__.__name__ == "DistributedSuitAI":
				if val.zoneId == 20 or val.getPlace() == CIGlobals.ToontownCentral:
					if val.__class__.__name__ == "DistributedSuitAI" and val.head == "vp" \
					and val.doId != self.distSuit.doId or val.__class__.__name__ == "DistributedToonAI":
						# We can be a medic and heal the fellow VP...
						if not val.isDead():
							if self.distSuit.getDistance(val) <= 40:
								toons.append(val)
		if toons == []:
			return
		toon = random.randint(0, len(toons) - 1)
		if self.head != "vp":
			self.AiBehaviors.pauseAi("pathfollow")
		self.distSuit.b_setAnimState("neutral")
		self.distSuit.headsUp(toons[toon])
		self.attackToon(toons[toon].__class__.__name__)
		self.setAttacking(True)
						
	def attackToon(self, type):
		attack = random.randint(0, 5)
		if attack == 0:
			self.attackName = "canned"
		elif attack == 1:
			self.attackName = "clipontie"
		elif attack == 2:
			self.attackName = "sacked"
		elif attack == 3:
			self.attackName = "glowerpower"
		elif attack == 4:
			self.attackName = "playhardball"
		elif attack == 5:
			self.attackName = "marketcrash"
		self.damageAmount = int(self.distSuit.maxHP / CIGlobals.SuitAttackDamageFactors[self.attackName])
		attackTaunt = random.randint(0, len(CIGlobals.SuitAttackTaunts[self.attackName]) - 1)
		self.distSuit.d_setAttack(CIGlobals.SuitAttacks[attack])
		if type == "DistributedSuitAI":
			self.distSuit.b_setChat(CIGlobals.SuitHealTaunt)
		else:
			self.distSuit.b_setChat(CIGlobals.SuitAttackTaunts[self.attackName][attackTaunt])
		self.distSuit.continuePathId = random.uniform(0, 101010101010)
		self.continuePathId = self.distSuit.continuePathId
		Sequence(Wait(5), Func(self.setAttacking, False)).start()
		taskMgr.doMethodLater(CIGlobals.SuitAttackLengths[self.attackName], self.continuePath, str(self.continuePathId))
			
	def setAttacking(self, value):
		self.isAttacking = value
	
	def getAttacking(self):
		return self.isAttacking
		
	def continuePath(self, task):
		# Create a new path for the Suit if they are stuck...
		if self.head != "vp":
			self.AiBehaviors.removeAi('pathfollow')
			taskMgr.add(self.createPath, "createPath")
		else:
			self.distSuit.b_setAnimState("neutral")
		return task.done
		
	def fixNan(self):
		self.AiBehaviors.removeAi('pathfollow')
		taskMgr.add(self.createPath, "createPath")
		
	def handleWeaponCollisions(self, entry):
		if self.distSuit.weapon_state == "start":
			return
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToonAI":
				if val.getPlace() == CIGlobals.ToontownCentral:
					if val.getKey() == toonNP.getKey():
						val.b_setDamage(self.damageAmount)
						taskMgr.doMethodLater(0.1, self.checkToonHealth, "checkToonHealth", extraArgs=[None, val])
			elif val.__class__.__name__ == "DistributedSuitAI":
				if val.getKey() == toonNP.getKey():
					if not val.getHealth() <= 0:
						val.b_addHealth(self.damageAmount)
		self.distSuit.b_handleWeaponTouch()
		
	def checkToonHealth(self, task, val):
		if val.isDead():
			self.suitVictory()

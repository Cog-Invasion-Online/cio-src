from lib.toontown.globals import ToontownGlobals
from direct.distributed.ClientRepository import ClientRepository
from lib.toontown.npc.MickeyNPCBase import MickeyNPCBase
from lib.toontown.npc.GoofyNPCBase import GoofyNPCBase
from lib.toontown.suit.SuitBase import *
from pandac.PandaModules import *
from direct.actor.Actor import *
from direct.gui.DirectGui import *
from direct.task import Task
from direct.showbase.Transitions import *
from direct.directnotify.DirectNotify import *
from direct.showbase import Audio3DManager
from direct.task import Task
import sys
import os
import random
from direct.distributed.PyDatagram import PyDatagram
import os
from lib.toontown.suit.SuitTournament import SuitTournament
from lib.toontown.hood.HoodUtil import HoodUtil
from lib.toontown.minigame.MinigameStationBase import MinigameStationBase
from pandac.PandaModules import UniqueIdAllocator

SUITS_ACTIVE = 25001
SUITS_INACTIVE = 25002
SYS_MSG = 50000
BOSS_SPAWNED = 25007
BOSS_ACTIVE = 25008

notify = DirectNotify().newCategory("AIRepository")

#render2d.hide()

host = base.config.GetString('server-address')
port = base.config.GetString('server-port')
url = URLSpec("http://%s:%s" % (host, port))

render.setAntialias(AntialiasAttrib.MMultisample)

class AIRepository:
	eventLoggerNotify = DirectNotify().newCategory("EventLogger")
	
	def __init__(self):
		base.cr = ClientRepository(dcFileNames = ['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'], dcSuffix = 'AI')
		base.cr.connect([url], successCallback = self.connectSuccess, failureCallback = self.connectFailure)
		base.cTrav = CollisionTraverser()
		self.skeleton = 0
		if base.config.GetBool('want-suits', True):
			base.accept("SpawnSuit", self.createSuit)
		self.activeInvasion = False
		self.invasionSize = 0
		self.difficulty = ""
		self.title = DirectLabel(text="Server Menu", pos=(-0.05, -0.1, -0.1), scale=0.1, relief=None, text_fg=(1,1,1,1), parent=base.a2dTopRight, text_align=TextNode.ARight)
		self.Suits = []
		base.pathNodes = []
		self.SuitCount = 0
		self.automaticSuits = 0
		self.hoodUtil = HoodUtil(base.cr)
		self.tournament = SuitTournament()
		self.lastChoice = None
		self.zoneAllocator = UniqueIdAllocator(50, 500)
		
	def allocateZone(self):
		return self.zoneAllocator.allocate()
		
	def freeZone(self, zone):
		self.zoneAllocator.free(zone)
		
	def logServerEvent(self, type, msg):
		self.eventLoggerNotify.info("%s: %s" % (type.upper(), msg))
		
	def killAllSuits(self):
		for suit in self.Suits:
			if not suit.distSuit.isDead() and suit.head != "vp":
				suit.distSuit.b_setHealth(0)
		
	def enableAutoSuits(self):
		self.automaticSuits = 1
		random_wait = random.uniform(5, 60)
		taskMgr.doMethodLater(random_wait, self.autoSuiter, "autoSuitSpawn")
		base.accept("control", self.disableAutoSuits)
		print "AutoSuit: Auto suits enabled."
		
	def disableAutoSuits(self):
		self.automaticSuits = 0
		taskMgr.remove("autoSuitSpawn")
		base.accept("control", self.enableAutoSuits)
		print "AutoSuit: Auto suits disabled."
		
	def isBossActive(self):
		for suit in self.Suits:
			if suit.head == "vp":
				return True
		return False
		
	def autoSuiter(self, task):
		random_choice = random.randint(0, 7)
		if self.lastChoice == 0 or self.lastChoice == 1 or self.lastChoice == 2 and self.SuitCount > 0:
			random_choice = random.randint(2, 6)
		elif self.lastChoice == 7:
			random_choice = random.randint(1, 6)
				
		if random_choice == 0 or random_choice == 1 or random_choice == 2:
			random_delay = random.randint(40, 80)
			choice = "invasion"
		elif random_choice == 3 or random_choice == 4 or random_choice == 5 or random_choice == 6:
			random_delay = random.randint(5, 20)
			choice = "suit"
		elif random_choice == 7:
			choice = "tournament"
			random_delay = random.randint(360, 700)
		self.lastChoice = random_choice
		if self.lastChoice == 7 and self.activeInvasion or self.SuitCount > 0:
			self.lastChoice = 1
			random_delay = random.randint(5, 80)
		if self.toonsAreInZone(20):
			self.createAutoSuit(choice)
			print "AutoSuit: Creating auto suit."
		else:
			random_delay = random.randint(20, 80)
			print "AutoSuit: Can't create an auto suit with no toons playing. Changing delay time."
		print "AutoSuit: Delay is %s seconds." % random_delay
		task.delayTime = random_delay
		return task.again
		
	def toonsArePlaying(self):
		for key in base.cr.doId2do.keys():
			obj = base.cr.doId2do[key]
			if obj.__class__.__name__ == "DistributedToon":
				return True
		return False
		
	def toonsAreInZone(self, zone):
		for key in base.cr.doId2do.keys():
			obj = base.cr.doId2do[key]
			if obj.__class__.__name__ == "DistributedToon":
				if obj.zoneId == zone:
					return True
		return False
		
	def createAutoSuit(self, choice):
		if choice == "invasion":
			if self.SuitCount < 20 and not self.tournament.inTournament and not self.activeInvasion:
				# Spawn invasion
				random_diff = random.randint(0, 2)
				if random_diff == 0:
					self.difficulty = "easy"
				elif random_diff == 1:
					self.diffiuclty = "normal"
				elif random_diff == 2:
					self.difficulty = "hard"
				random_size = random.randint(0, 2)
				if random_size == 0:
					self.size = "small"
				elif random_size == 1:
					self.size = "medium"
				elif random_size == 2:
					self.size = "large"
				self.suit = "ABC"
				taskMgr.add(self.startInvasion, "startInvasion", extraArgs=[0], appendTask=True)
		elif choice == "suit":
			if self.SuitCount < 25 and not self.tournament.inTournament:
				# Spawn suit
				random_type = random.randint(0, 2)
				if random_type == 0:
					type = "A"
				elif random_type == 1:
					type = "B"
				elif random_type == 2:
					type = "C"
				self.createSuit(type)
		elif choice == "tournament":
			if self.SuitCount == 0 and not self.tournament.inTournament and not self.activeInvasion:
				# Spawn tournament
				self.tournament.initiateTournament()
			else:
				self.lastChoice = 1
				
		return None
		
	def callBackup(self, difficulty):
		self.difficulty = difficulty
		self.suit = "ABC"
		self.size = "medium"
		self.killAllSuits()
		taskMgr.doMethodLater(8, self.startInvasion, "startBackupInvasion", extraArgs=[1], appendTask=True)
		
	def sendSysMessage(self, textEntered):
		pkg = PyDatagram()
		pkg.addUint16(SYS_MSG)
		pkg.addString("SYSTEM: " + textEntered)
		base.sr.sendDatagram(pkg)
		
	def connectFailure(self):
		notify.warning("failure connecting to gameserver, AI server will not initiate.")
		
	def connectSuccess(self):
		base.acceptOnce('createReady', self.createReady)
		
	def startInvasion(self, skeleton, task):
		if not self.activeInvasion and not self.tournament.inTournament:
			self.sendSysMessage("A " + ToontownGlobals.Suit + " Invasion has begun in Toontown Central!!!")
		self.activeInvasion = True
		if self.isFullInvasion():
			return Task.done
		
		suitsNow = random.randint(0, 7)
		for suit in range(suitsNow):
			if self.isFullInvasion():
				break
			if self.suit == "ABC":
				random_suitType = random.randint(0, 2)
				if random_suitType == 0:
					self.createSuit("A", skeleton = skeleton)
				elif random_suitType == 1:
					self.createSuit("B", skeleton = skeleton)
				elif random_suitType == 2:
					self.createSuit("C", skeleton = skeleton)
			else:
				self.createSuit(self.suit, skeleton = skeleton)
			
		task.delayTime = 4
		return Task.again
		
	def isFullInvasion(self):
		if self.size == "large":
			if self.SuitCount >= 20:
				return True
			else:
				return False
		elif self.size == "medium":
			if self.SuitCount >= 13:
				return True
			else:
				return False
		elif self.size == "small":
			if self.SuitCount >= 5:
				return True
			else:
				return False
		
	def createReady(self):
		self.hoodUtil.load("TT", AI=1)
		base.cr.setInterestZones([10, 20, 30])
		self.timeMgr = base.cr.createDistributedObject(className="TimeManagerAI", zoneId=10)
		self.createCChars()
		self.createMinigames()
		
	def createCChars(self):
		if base.config.GetBool('want-classic-chars', True):
			if base.config.GetBool('want-mickey', True):
				MickeyNPCBase(base.cr)
			if base.config.GetBool('want-goofy', True):
				GoofyNPCBase(base.cr)
				
	def createMinigames(self):
		if base.config.GetBool('want-minigames', True):
			if base.config.GetBool('want-race-game', True):
				mg1 = base.cr.createDistributedObject(className="DistributedMinigameStationAI", zoneId=30)
				mg1.b_setStation(ToontownGlobals.RaceGame)
				mg1.b_setLocationPoint(0)
			if base.config.GetBool('want-uno-game', True):
				mg2 = base.cr.createDistributedObject(className="DistributedMinigameStationAI", zoneId=30)
				mg2.b_setStation(ToontownGlobals.UnoGame)
				mg2.b_setLocationPoint(1)
			if base.config.GetBool('want-sneaky-game', True):
				mg3 = base.cr.createDistributedObject(className="DistributedMinigameStationAI", zoneId=30)
				mg3.b_setStation(ToontownGlobals.SneakyGame)
				mg3.b_setLocationPoint(2)
		
	def createSuit(self, type, head = None, team = None, anySuit = 1, skeleton = 0):
		if self.SuitCount == 0 and not self.activeInvasion and not self.tournament.inTournament:
			self.sendSysMessage("A " + ToontownGlobals.Suit + " is flying down in Toontown Central!")
		self.SuitCount += 1
		if not self.activeInvasion:
			self.invasionSize = 0
		if self.SuitCount == 1:
			if self.tournament.inTournament:
				if self.tournament.getRound() == 1:
					self.hoodUtil.enableSuitEffect(0)
					pkg = PyDatagram()
					pkg.addUint16(SUITS_ACTIVE)
					pkg.addUint32(self.invasionSize)
					base.sr.sendDatagram(pkg)
			else:
				self.hoodUtil.enableSuitEffect(0)
				pkg = PyDatagram()
				pkg.addUint16(SUITS_ACTIVE)
				pkg.addUint32(self.invasionSize)
				base.sr.sendDatagram(pkg)
		if anySuit:
			if self.difficulty == "hard":
				if type == "B":
					self.random_head = random.randint(7, 8)
				elif type == "C":
					self.random_head = random.randint(7, 8)
				elif type == "A":
					self.random_head = random.randint(8, 13)
			elif self.difficulty == "normal":
				if type == "B":
					self.random_head = random.randint(3, 6)
				elif type == "C":
					self.random_head = random.randint(4, 6)
				elif type == "A":
					self.random_head = random.randint(4, 7)
			elif self.difficulty == "easy":
				if type == "B":
					self.random_head = random.randint(0, 2)
				elif type == "C":
					self.random_head = random.randint(0, 3)
				elif type == "A":
					self.random_head = random.randint(0, 3)
			elif self.difficulty == "all" or self.difficulty == "":
				if type == "B" or type == "C":
					self.random_head = random.randint(0, 8)
				elif type == "A":
					self.random_head = random.randint(0, 13)
			if type == "C":
				if self.random_head == 0:
					head = 'coldcaller'
					team = 's'
				elif self.random_head == 1:
					head = 'shortchange'
					team = 'm'
				elif self.random_head == 2:
					head = 'bottomfeeder'
					team = 'l'
				elif self.random_head == 3:
					head = 'flunky'
					team = 'c'
				elif self.random_head == 4:
					head = 'tightwad'
					team = 'm'
				elif self.random_head == 5:
					head = 'micromanager'
					team = 'c'
				elif self.random_head == 6:
					head = 'gladhander'
					team = 's'
				elif self.random_head == 7:
					head = 'moneybags'
					team = 'm'
				elif self.random_head == 8:
					head = 'corporateraider'
					team = 'c'
			if type == "B":
				if self.random_head == 0:
					head = 'pencilpusher'
					team = 'c'
				elif self.random_head == 1:
					head = 'bloodsucker'
					team = 'l'
				elif self.random_head == 2:
					head = 'telemarketer'
					team = 's'
				elif self.random_head == 3:
					head = 'ambulancechaser'
					team = 'l'
				elif self.random_head == 4:
					head = 'beancounter'
					team = 'm'
				elif self.random_head == 5:
					head = 'downsizer'
					team = 'c'
				elif self.random_head == 6:
					head = 'movershaker'
					team = 's'
				elif self.random_head == 7:
					head = 'spindoctor'
					team = 'l'
				elif self.random_head == 8:
					head = 'loanshark'
					team = 'm'
			if type == "A":
				if self.random_head == 0:
					head = 'pennypincher'
					team = 'm'
				elif self.random_head == 1:
					head = 'yesman'
					team = 'c'
				elif self.random_head == 2:
					head = 'doubletalker'
					team = 'l'
				elif self.random_head == 3:
					head = 'namedropper'
					team = 's'
				elif self.random_head == 4:
					head = 'backstabber'
					team = 'l'
				elif self.random_head == 5:
					head = 'numbercruncher'
					team = 'm'
				elif self.random_head == 6:
					head = 'headhunter'
					team = 'c'
				elif self.random_head == 7:
					head = 'twoface'
					team = 's'
				elif self.random_head == 8:
					head = 'legaleagle'
					team = 'l'
				elif self.random_head == 9:
					head = 'mingler'
					team = 's'
				elif self.random_head == 10:
					head = 'bigcheese'
					team = 'c'
				elif self.random_head == 11:
					head = 'bigwig'
					team = 'l'
				elif self.random_head == 12:
					head = 'robberbaron'
					team = 'm'
				elif self.random_head == 13:
					head = 'mrhollywood'
					team = 's'
		if head == "vp":
			self.handleBossSpawned()
		SuitBase(base.cr, type, head, team, skeleton)
		
	def handleBossSpawned(self):
		bosses = 0
		for suit in self.Suits:
			if suit.head == "vp":
				bosses += 1
		if bosses == 0:
			self.sendBossSpawned()
			
	def sendBossSpawned(self):
		pkg = PyDatagram()
		pkg.addUint16(BOSS_SPAWNED)
		base.sr.sendDatagram(pkg)
		
	def deadSuit(self):
		self.SuitCount -= 1
		if self.SuitCount < 0:
			self.SuitCount = 0
		if self.tournament.inTournament:
			self.tournament.handleDeadSuit()
			return
		if self.SuitCount == 0:
			if self.activeInvasion:
				self.activeInvasion = False
			self.hoodUtil.disableSuitEffect()
			pkg = PyDatagram()
			pkg.addUint16(SUITS_INACTIVE)
			base.sr.sendDatagram(pkg)

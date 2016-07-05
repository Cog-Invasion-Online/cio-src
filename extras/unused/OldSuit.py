"""

  Filename: Suit.py
  Created by: blach (??July14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.avatar import Avatar
from direct.directnotify.DirectNotify import *
from direct.gui.DirectGui import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.showbase import Audio3DManager
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.actor.Actor import Actor
from direct.showbase.ShadowPlacer import ShadowPlacer
from direct.interval.ProjectileInterval import ProjectileInterval
from lib.coginvasion.toon import ParticleLoader
from direct.task.Task import Task
from direct.interval.IntervalGlobal import *
import random

audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
audio3d.setDistanceFactor(25)
notify = DirectNotify().newCategory("Suit")

class Suit(Avatar.Avatar):
	healthColors = (Vec4(0, 1, 0, 1),
		Vec4(1, 1, 0, 1),
		Vec4(1, 0.5, 0, 1),
		Vec4(1, 0, 0, 1),
		Vec4(0.3, 0.3, 0.3, 1))
	healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
		Vec4(1, 1, 0.25, 0.5),
		Vec4(1, 0.5, 0.25, 0.5),
		Vec4(1, 0.25, 0.25, 0.5),
		Vec4(0.3, 0.3, 0.3, 0))
	medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
		's': Vec4(0.843, 0.745, 0.745, 1.0),
		'l': Vec4(0.749, 0.776, 0.824, 1.0),
		'm': Vec4(0.749, 0.769, 0.749, 1.0)}
	health2DmgMultiplier = 2.5
	
	def __init__(self):
		try:
			self.Suit_initialized
			return
		except:
			self.Suit_initialized = 1
		
		Avatar.Avatar.__init__(self)
		self.avatarType = CIGlobals.Suit
		self.name = ''
		self.chat = ''
		self.suit = None
		self.suitHeads = None
		self.suitHead = None
		self.loserSuit = None
		self.healthMeterGlow = None
		self.healthMeter = None
		self.weapon = None
		self.weapon_sfx = None
		self.anim = None
		self.suit_dial = None
		self.shadow = None
		self.balloon_sfx = None
		self.add_sfx = None
		self.explosion = None
		self.largeExp = None
		self.smallExp = None
		self.death_sfx = None
		self.attack = None
		self.wtrajectory = None
		self.throwObjectId = None
		self.hasSpawned = False
		self.condition = 0
		self.type = ""
		self.head = ""
		self.team = ""
		self.isSkele = 0
		self.animFSM = ClassicFSM('Suit', [State('off', self.enterOff, self.exitOff),
								State('neutral', self.enterNeutral, self.exitNeutral),
								State('walk', self.enterWalk, self.exitWalk),
								State('die', self.enterDie, self.exitDie),
								State('attack', self.enterAttack, self.exitAttack),
								State('flydown', self.enterFlyDown, self.exitFlyDown),
								State('pie', self.enterPie, self.exitPie),
								State('win', self.enterWin, self.exitWin),
								State('flyaway', self.enterFlyAway, self.exitFlyAway),
								State('rollodex', self.enterRollodex, self.exitRollodex)], 'off', 'off')
		animStateList = self.animFSM.getStates()
		self.animFSM.enterInitialState()
		
		self.initializeBodyCollisions()
		
	def delete(self):
		try:
			self.Suit_deleted
		except:
			self.Suit_deleted = 1
			if self.suit:
				self.cleanupSuit()
			if self.loserSuit:
				self.cleanupLoserSuit()
			if self.suitHeads:
				self.suitHeads.remove()
				self.suitHeads = None
			if self.suitHead:
				self.suitHead.remove()
				self.suitHead = None
			if self.healthMeterGlow:
				self.healthMeterGlow.remove()
				self.healthMeterGlow = None
			if self.healthMeter:
				self.healthMeter.remove()
				self.healthMeter = None
			if self.shadow:
				self.shadow.remove()
				self.shadow = None
			self.weapon = None
			self.weapon_sfx = None
			self.suit_dial = None
			del self.shadowPlacer
			
	def generateSuit(self, suitType, suitHead, suitTeam, suitHealth, skeleton):
		self.health = suitHealth
		self.maxHealth = suitHealth
		self.generateBody(suitType, suitTeam, suitHead, skeleton)
		self.generateHealthMeter()
		self.generateHead(suitType, suitHead)
		self.setupNameTag()
		Avatar.Avatar.initShadow(self)
		
	def generateBody(self, suitType, suitTeam, suitHead, skeleton):
		if self.suit:
			self.cleanupSuit()
			
		self.team = suitTeam
		self.type = suitType
		self.head = suitHead
		self.isSkele = skeleton
		
		if suitType == "A":
			if skeleton:
				self.suit = Actor("phase_5/models/char/cogA_robot-zero.bam")
			else:
				self.suit = Actor("phase_3.5/models/char/suitA-mod.bam")
			self.suit.loadAnims({"neutral": "phase_4/models/char/suitA-neutral.bam",
							"walk": "phase_4/models/char/suitA-walk.bam",
							"pie": "phase_4/models/char/suitA-pie-small.bam",
							"land": "phase_5/models/char/suitA-landing.bam",
							"throw-object": "phase_5/models/char/suitA-throw-object.bam",
							"throw-paper": "phase_5/models/char/suitA-throw-paper.bam",
							"glower": "phase_5/models/char/suitA-glower.bam",
							"win": "phase_4/models/char/suitA-victory.bam",
							"rollodex": "phase_5/models/char/suitA-roll-o-dex.bam"})
		if suitType == "B":
			if skeleton:
				self.suit = Actor("phase_5/models/char/cogB_robot-zero.bam")
			else:
				self.suit = Actor("phase_3.5/models/char/suitB-mod.bam")
			self.suit.loadAnims({"neutral": "phase_4/models/char/suitB-neutral.bam",
							"walk": "phase_4/models/char/suitB-walk.bam",
							"pie": "phase_4/models/char/suitB-pie-small.bam",
							"land": "phase_5/models/char/suitB-landing.bam",
							"throw-object": "phase_5/models/char/suitB-throw-object.bam",
							"throw-paper": "phase_5/models/char/suitB-throw-paper.bam",
							"glower": "phase_5/models/char/suitB-magic1.bam",
							"win": "phase_4/models/char/suitB-victory.bam",
							"rollodex": "phase_5/models/char/suitB-roll-o-dex.bam"})
		if suitType == "C":
			if skeleton:
				self.suit = Actor("phase_5/models/char/cogC_robot-zero.bam")
			else:
				self.suit = Actor("phase_3.5/models/char/suitC-mod.bam")
			self.suit.loadAnims({"neutral": "phase_3.5/models/char/suitC-neutral.bam",
						"walk": "phase_3.5/models/char/suitC-walk.bam",
						"pie": "phase_3.5/models/char/suitC-pie-small.bam",
						"land": "phase_5/models/char/suitC-landing.bam",
						"throw-object": "phase_3.5/models/char/suitC-throw-paper.bam",
						"throw-paper": "phase_3.5/models/char/suitC-throw-paper.bam",
						"glower": "phase_5/models/char/suitC-glower.bam",
						"win": "phase_4/models/char/suitC-victory.bam"})
		if skeleton:
			self.suit.setTwoSided(1)
		self.suit.getGeomNode().setScale(CIGlobals.SuitScales[suitHead] / CIGlobals.SuitScaleFactors[suitType])
		
		if skeleton:
			if suitTeam == "s":
				self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_sales.jpg")
			elif suitTeam == "m":
				self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_money.jpg")
			elif suitTeam == "l":
				self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_legal.jpg")
			elif suitTeam == "c":
				self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_boss.jpg")
			self.suit.find('**/tie').setTexture(self.suit_tie, 1)
		else:
			self.suit_blazer = loader.loadTexture("phase_3.5/maps/" + suitTeam + "_blazer.jpg")
			self.suit_leg = loader.loadTexture("phase_3.5/maps/" + suitTeam + "_leg.jpg")
			self.suit_sleeve = loader.loadTexture("phase_3.5/maps/" + suitTeam + "_sleeve.jpg")
			
			self.suit.find('**/legs').setTexture(self.suit_leg, 1)
			self.suit.find('**/arms').setTexture(self.suit_sleeve, 1)
			self.suit.find('**/torso').setTexture(self.suit_blazer, 1)
		
			if suitHead == "coldcaller":
				self.suit.find('**/hands').setColor(0.55, 0.65, 1.0, 1.0)
			elif suitHead == "corporateraider":
				self.suit.find('**/hands').setColor(0.85, 0.55, 0.55, 1.0)
			elif suitHead == "bigcheese":
				self.suit.find('**/hands').setColor(0.75, 0.95, 0.75, 1.0)
			elif suitHead == "bloodsucker":
				self.suit.find('**/hands').setColor(0.95, 0.95, 1.0, 1.0)
			elif suitHead == "spindoctor":
				self.suit.find('**/hands').setColor(0.5, 0.8, 0.75, 1.0)
			elif suitHead == "legaleagle":
				self.suit.find('**/hands').setColor(0.25, 0.25, 0.5, 1.0)
			elif suitHead == "pennypincher":
				self.suit.find('**/hands').setColor(1.0, 0.5, 0.6, 1.0)
			elif suitHead == "loanshark":
				self.suit.find('**/hands').setColor(0.5, 0.85, 0.75, 1.0)
			else:
				self.suit.find('**/hands').setColor(CIGlobals.SuitHandColors[suitTeam])
		
		self.suit.reparentTo(self)
		
	def generateHead(self, suitType, suitHead):
		if self.suitHead:
			self.cleanupSuitHead()
			
		self.type = suitType
		self.head = suitHead
		
		if suitHead == "vp":
			self.suitHead = Actor("phase_9/models/char/sellbotBoss-head-zero.bam",
								{"neutral": "phase_9/models/char/bossCog-head-Ff_neutral.bam"})
			self.suitHead.setTwoSided(True)
			self.suitHead.loop("neutral")
			self.suitHead.setScale(0.35)
			self.suitHead.setHpr(270, 0, 270)
			self.suitHead.setZ(-0.10)
		else:
			if suitType == "A" or suitType == "B":
				self.suitHeads = loader.loadModel("phase_4/models/char/suit" + suitType + "-heads.bam")
			else:
				self.suitHeads = loader.loadModel("phase_3.5/models/char/suit" + suitType + "-heads.bam")
			self.suitHead = self.suitHeads.find('**/' + CIGlobals.SuitHeads[suitHead])
			if suitHead == "flunky":
				glasses = self.suitHeads.find('**/glasses')
				glasses.reparentTo(self.suitHead)
				glasses.setTwoSided(True)
			if suitHead in CIGlobals.SuitSharedHeads:
				if suitHead == "coldcaller":
					self.suitHead.setColor(0.25, 0.35, 1.0, 1.0)
				else:
					headTexture = loader.loadTexture("phase_3.5/maps/" + suitHead + ".jpg")
					self.suitHead.setTexture(headTexture, 1)
		if not self.isSkele:
			self.suitHead.reparentTo(self.suit.find('**/joint_head'))
			
	def cleanupSuit(self):
		if self.shadow:
			self.shadow.remove()
			self.shadow = None
		self.removeHealthBar()
		self.suit.cleanup()
		self.suit = None
		
	def cleanupSuitHead(self):
		if self.suitHeads:
			self.suitHeads.remove()
			self.suitHeads = None
		if self.suitHead:
			self.suitHead.remove()
			self.suitHead = None
		
	def cleanupLoserSuit(self):
		if self.explosion:
			self.explosion.remove()
			self.explosion = None
		if self.smallExp:
			self.smallExp = None
		if self.largeExp:
			self.largeExp.cleanup()
			self.largeExp = None
		if self.loserSuit:
			self.loserSuit.cleanup()
			self.loserSuit = None
		
	def setName(self, nameString, charName):
		Avatar.Avatar.setName(self, nameString, avatarType=self.avatarType, charName=charName)
		
	def setChat(self, chatString):
		self.chat = chatString
		if self.isSkele:
			if "?" in chatString:
				self.suit_dial = audio3d.loadSfx("phase_5/audio/sfx/Skel_COG_VO_question.ogg")
			elif "!" in chatString:
				self.suit_dial = audio3d.loadSfx("phase_5/audio/sfx/Skel_COG_VO_grunt.ogg")
			else:
				self.suit_dial = audio3d.loadSfx("phase_5/audio/sfx/Skel_COG_VO_statement.ogg")
		elif self.head == "vp":
			if "?" in chatString:
				self.suit_dial = audio3d.loadSfx("phase_9/audio/sfx/Boss_COG_VO_question.ogg")
			elif "!" in chatString:
				self.suit_dial = audio3d.loadSfx("phase_9/audio/sfx/Boss_COG_VO_grunt.ogg")
			else:
				self.suit_dial = audio3d.loadSfx("phase_9/audio/sfx/Boss_COG_VO_statement.ogg")
		else:
			if "?" in chatString:
				self.suit_dial = audio3d.loadSfx("phase_3.5/audio/dial/COG_VO_question.ogg")
			elif "!" in chatString:
				self.suit_dial = audio3d.loadSfx("phase_3.5/audio/dial/COG_VO_grunt.ogg")
			else:
				self.suit_dial = audio3d.loadSfx("phase_3.5/audio/dial/COG_VO_statement.ogg")
		if self.isSkele:
			audio3d.attachSoundToObject(self.suit_dial, self.suit)
		else:
			audio3d.attachSoundToObject(self.suit_dial, self.suitHead)
		self.suit_dial.play()
		Avatar.Avatar.setChat(self, chatString)
		
	def generateHealthMeter(self):
		self.removeHealthBar()
		model = loader.loadModel("phase_3.5/models/gui/matching_game_gui.bam")
		button = model.find('**/minnieCircle')
		button.setScale(3.0)
		button.setH(180)
		button.setColor(self.healthColors[0])
		chestNull = self.suit.find('**/def_joint_attachMeter')
		if chestNull.isEmpty():
			chestNull = self.suit.find('**/joint_attachMeter')
		button.reparentTo(chestNull)
		self.healthBar = button
		glow = loader.loadModel("phase_3.5/models/props/glow.bam")
		glow.reparentTo(self.healthBar)
		glow.setScale(0.28)
		glow.setPos(-0.005, 0.01, 0.015)
		glow.setColor(self.healthGlowColors[0])
		button.flattenLight()
		self.healthBarGlow = glow
		self.condition = 0
		
	def updateHealthBar(self, hp):
		if hp > self.hp:
			self.hp = hp
		self.hp -= hp
		health = float(self.health) / float(self.maxHP)
		if health > 0.95:
			condition = 0
		elif health > 0.7:
			condition = 1
		elif health > 0.3:
			condition = 2
		elif health > 0.05:
			condition = 3
		elif health > 0.0:
			condition = 4
		else:
			condition = 5
			
		if self.condition != condition:
			if condition == 4:
				blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
				taskMgr.add(blinkTask, self.taskName('blink-task'))
			elif condition == 5:
				if self.condition == 4:
					taskMgr.remove(self.taskName('blink-task'))
				blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
				taskMgr.add(blinkTask, self.taskName('blink-task'))
			else:
				self.healthBar.setColor(self.healthColors[condition], 1)
				self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
			self.condition = condition
			
	def __blinkRed(self, task):
		self.healthBar.setColor(self.healthColors[3], 1)
		self.healthBarGlow.setColor(self.healthGlowColors[3], 1)
		if self.condition == 5:
			self.healthBar.setScale(1.17)
		return Task.done
		
	def __blinkGray(self, task):
		if not self.healthBar:
			return
		self.healthBar.setColor(self.healthColors[4], 1)
		self.healthBarGlow.setColor(self.healthGlowColors[4], 1)
		if self.condition == 5:
			self.healthBar.setScale(1.0)
		return Task.done
		
	def removeHealthBar(self):
		if self.healthMeter:
			self.healthBar.removeNode()
			self.healthBar = None
		if self.condition == 4 or self.condition == 5:
			taskMgr.remove(self.taskName('blink-task'))
		self.healthCondition = 0
		return
			
	def enterOff(self):
		self.anim = None
		return
		
	def exitOff(self):
		pass
		
	def exitGeneral(self):
		self.suit.stop()
		
	def enterNeutral(self):
		self.suit.loop("neutral")
		
	def exitNeutral(self):
		self.exitGeneral()
		
	def enterRollodex(self):
		self.suit.play("rollodex")
		
	def exitRollodex(self):
		self.exitGeneral()
		
	def enterWalk(self):
		self.suit.loop("walk")
		
	def exitWalk(self):
		self.exitGeneral()
		
	def generateLoserSuit(self):
		self.cleanupLoserSuit()
		if self.type == "A":
			if self.isSkele:
				self.loserSuit = Actor("phase_5/models/char/cogA_robot-lose-mod.bam")
			else:
				self.loserSuit = Actor("phase_4/models/char/suitA-lose-mod.bam")
			self.loserSuit.loadAnims({"lose": "phase_4/models/char/suitA-lose.bam"})
		if self.type == "B":
			if self.isSkele:
				self.loserSuit = Actor("phase_5/models/char/cogB_robot-lose-mod.bam")
			else:
				self.loserSuit = Actor("phase_4/models/char/suitB-lose-mod.bam")
			self.loserSuit.loadAnims({"lose": "phase_4/models/char/suitB-lose.bam"})
		if self.type == "C":
			if self.isSkele:
				self.loserSuit = Actor("phase_5/models/char/cogC_robot-lose-mod.bam")
			else:
				self.loserSuit = Actor("phase_3.5/models/char/suitC-lose-mod.bam")
			self.loserSuit.loadAnims({"lose": "phase_3.5/models/char/suitC-lose.bam"})
		if self.isSkele:
			self.loserSuit.find('**/tie').setTexture(self.suit_tie, 1)
			self.loserSuit.setTwoSided(1)
		else:
			self.loserSuit.find('**/hands').setColor(self.suit.find('**/hands').getColor())
			self.loserSuit.find('**/legs').setTexture(self.suit_leg, 1)
			self.loserSuit.find('**/arms').setTexture(self.suit_sleeve, 1)
			self.loserSuit.find('**/torso').setTexture(self.suit_blazer, 1)
		self.loserSuit.getGeomNode().setScale(self.suit.getScale())
		self.loserSuit.reparentTo(self)
		if not self.isSkele:
			self.suitHead.reparentTo(self.loserSuit.find('**/joint_head'))
		self.loserSuit.setPos(self.suit.getPos(render))
		self.loserSuit.setHpr(self.suit.getHpr(render))
		self.cleanupSuit()
		Avatar.Avatar.initShadow(self, self.avatarType)
		self.loserSuit.reparentTo(render)
		
	def enterDie(self):
		self.generateLoserSuit()
		self.state = "dead"
		self.loserSuit.play("lose")
		spinningSound = base.loadSfx("phase_3.5/audio/sfx/Cog_Death.ogg")
		deathSound = base.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.ogg")
		#audio3d.attachSoundToObject(spinningSound, self.loserSuit)
		#audio3d.attachSoundToObject(deathSound, self.loserSuit)
		Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.4, node=self.loserSuit),
			SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=2.0, node=self.loserSuit),
			SoundInterval(deathSound, volume=0.32, node=self.loserSuit)).start()
		Sequence(Wait(0.8), Func(self.smallDeathParticles), Wait(4.2), Func(self.suitExplode),
				Wait(1.0), Func(self.delSuit)).start()
		
	def smallDeathParticles(self):
		self.smallExp = ParticleLoader.loadParticleEffect("phase_3.5/etc/gearExplosionSmall.ptf")
		self.smallExp.start(self.loserSuit)
		
	def suitExplode(self):
		self.smallExp.cleanup()
		self.largeExp = ParticleLoader.loadParticleEffect("phase_3.5/etc/gearExplosion.ptf")
		self.largeExp.start(self.loserSuit)
		self.explosion = loader.loadModel("phase_3.5/models/props/explosion.bam")
		self.explosion.setScale(0.5)
		self.explosion.reparentTo(render)
		self.explosion.setBillboardPointEye()
		if self.isSkele:
			self.explosion.setPos(self.loserSuit.find('**/joint_head').getPos(render) + (0, 0, 2))
		else:
			self.explosion.setPos(self.suitHead.getPos(render) + (0,0,2))
		
	def delSuit(self):
		self.cleanupLoserSuit()
		self.disableBodyCollisions()
		
	def exitDie(self):
		pass
		
	def enterFlyDown(self):
		self.fd_sfx = audio3d.loadSfx("phase_5/audio/sfx/ENC_propeller_in.ogg")
		self.prop = Actor("phase_4/models/props/propeller-mod.bam",
						{"chan": "phase_4/models/props/propeller-chan.bam"})
		audio3d.attachSoundToObject(self.fd_sfx, self.prop)
		self.fd_sfx.play()
		self.prop.reparentTo(self.suit.find('**/joint_head'))
		propTrack = Sequence(Func(self.prop.loop, 'chan', fromFrame=0, toFrame=3),
							Wait(1.75),
							Func(self.prop.play, 'chan', fromFrame=3))
		propTrack.start()
		if not self.hasSpawned:
			showSuit = Task.sequence(Task(self.hideSuit), Task.pause(0.3), Task(self.showSuit))
			taskMgr.add(showSuit, "showsuit")
			self.hasSpawned = True
		dur = self.suit.getDuration('land')
		suitTrack = Sequence(Func(self.suit.pose, 'land', 0),
							Wait(1.9),
							ActorInterval(self.suit, 'land', duration=dur))
		suitTrack.start()
		
	def hideSuit(self, task):
		self.hide()
		return Task.done
	
	def showSuit(self, task):
		self.show()
		fadeIn = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(0.6, colorScale=Vec4(1,1,1,1), startColorScale=Vec4(1,1,1,0)), Func(self.clearColorScale), Func(self.clearTransparency), Func(self.reparentTo, render))
		fadeIn.start()
		return Task.done
		
	def initializeLocalCollisions(self, name):
		Avatar.Avatar.initializeLocalCollisions(self, 1, 3, name)
		
	def initializeBodyCollisions(self):
		Avatar.Avatar.initializeBodyCollisions(self, self.avatarType, 2.25, 1, 4, 2)
		self.initializeRay(self.avatarType)
		self.collTube.setTangible(0)
		
	def deleteBean(self):
		if self.bean:
			self.bean.remove_node()
			self.bean = None
			
	def createJellyBean(self):
		self.deleteBean()
		money = int(self.maxHP / CIGlobals.SuitAttackDamageFactors['clipontie'])
		if money == 1:
			self.bean = loader.loadModel("phase_5.5/models/estate/jellyBean.bam")
			self.bean.set_two_sided(True)
			random_r = random.uniform(0, 1)
			random_g = random.uniform(0, 1)
			random_b = random.uniform(0, 1)
			self.bean.set_color(random_r, random_g, random_b, 1)
		else:
			self.bean = loader.loadModel("phase_5.5/models/estate/jellybeanJar.bam")
		self.bean.reparent_to(render)
		self.bean.set_pos(self.get_pos(render) + (0, 0, 1))
		bean_int = self.bean.hprInterval(1,
										Point3(360, 0, 0),
										startHpr=(0, 0, 0))
		bean_int.loop()
		
	def exitFlyDown(self):
		audio3d.detachSound(self.fd_sfx)
		self.prop.cleanup()
		self.prop = None
		
	def enterFlyAway(self):
		self.fa_sfx = audio3d.loadSfx("phase_5/audio/sfx/ENC_propeller_out.ogg")
		self.prop = Actor("phase_4/models/props/propeller-mod.bam",
						{"chan": "phase_4/models/props/propeller-chan.bam"})
		audio3d.attachSoundToObject(self.fa_sfx, self.prop)
		self.fa_sfx.play()
		self.prop.reparentTo(self.suit.find('**/joint_head'))
		self.prop.setPlayRate(-1.0, "chan")
		propTrack = Sequence(Func(self.prop.play, 'chan', fromFrame=3),
							Wait(1.75),
							Func(self.prop.play, 'chan', fromFrame=0, toFrame=3))
		propTrack.start()
		self.suit.setPlayRate(-1.0, 'land')
		self.suit.play('land')
		
	def exitFlyAway(self):
		audio3d.detachSound(self.fa_sfx)
		self.prop.cleanup()
		self.prop = None
		
	def enterAttack(self, attack):
		self.attack = attack
		
		self.weapon_state = 'start'
		
		if attack == "canned":
			self.weapon = loader.loadModel("phase_5/models/props/can.bam")
			self.weapon.setScale(15)
			self.weapon.setR(180)
			self.wss = CollisionSphere(0,0,0,0.05)
		elif attack == "clipontie":
			self.weapon = loader.loadModel("phase_5/models/props/power-tie.bam")
			self.weapon.setScale(4)
			self.weapon.setR(180)
			self.wss = CollisionSphere(0,0,0,0.2)
		elif attack == "sacked":
			self.weapon = loader.loadModel("phase_5/models/props/sandbag-mod.bam")
			self.weapon.setScale(2)
			self.weapon.setR(180)
			self.weapon.setP(90)
			self.weapon.setY(-2.8)
			self.weapon.setZ(-0.3)
			self.wss = CollisionSphere(0,0,0,1)
		elif attack == "playhardball":
			self.weapon = loader.loadModel("phase_5/models/props/baseball.bam")
			self.weapon.setScale(10)
			self.wss = CollisionSphere(0,0,0,0.1)
			self.weapon.setZ(-0.5)
		elif attack == "marketcrash":
			self.weapon = loader.loadModel("phase_5/models/props/newspaper.bam")
			self.weapon.setScale(3)
			self.weapon.setPos(0.41, -0.06, -0.06)
			self.weapon.setHpr(90, 0, 270)
			self.wss = CollisionSphere(0,0,0,0.35)
		elif attack == "glowerpower":
			self.weapon = loader.loadModel("phase_5/models/props/dagger.bam")
			self.wss = CollisionSphere(0,0,0,1)
		else:
			notify.warning("unknown attack!")
			
		self.throwObjectId = random.uniform(0, 101010101010)
		
		if attack == "canned" or attack == "playhardball":
			self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
			if self.type == "C":
				taskMgr.doMethodLater(2.2, self.throwObject, "throwObject" + str(self.throwObjectId))
			else:
				taskMgr.doMethodLater(3, self.throwObject, "throwObject" + str(self.throwObjectId))
			self.suit.play("throw-object")
		elif attack == "clipontie" or attack == "marketcrash" or attack == "sacked":
			self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
			if self.type == "C":
				taskMgr.doMethodLater(2.2, self.throwObject, "throwObject" + str(self.throwObjectId))
			else:
				taskMgr.doMethodLater(3, self.throwObject, "throwObject" + str(self.throwObjectId))
			self.suit.play("throw-paper")
		elif attack == "glowerpower":
			taskMgr.doMethodLater(1, self.throwObject, "throwObject" + str(self.throwObjectId))
			self.suit.play("glower")
		self.weaponSensorId = random.uniform(0, 1010101010101001)
		wsnode = CollisionNode('weaponSensor' + str(self.weaponSensorId))
		wsnode.addSolid(self.wss)
		self.wsnp = self.weapon.attachNewNode(wsnode)
		if attack == "sacked":
			self.wsnp.setZ(1)
		elif attack == "marketcrash":
			self.wsnp.setPos(-0.25, 0.3, 0)
			
	def delWeapon(self, task):
		if self.weapon:
			self.weapon.removeNode()
			self.weapon = None
		return task.done
		
	def interruptAttack(self):
		if self.wtrajectory:
			if self.wtrajectory.isStopped():
				if self.weapon:
					self.weapon.removeNode()
					self.weapon = None
		if self.throwObjectId:
			taskMgr.remove("throwObject" + str(self.throwObjectId))
		
	def handleWeaponTouch(self):
		if not self.attack == "glowerpower" or not self.attack == "clipontie":
			if self.weapon_sfx:
				self.weapon_sfx.stop()
		try: self.wtrajectory.pause()
		except: pass
		if self.weapon:
			self.weapon.removeNode()
			self.weapon = None
		
	def weaponCollisions(self):
		self.wsnp.setCollideMask(BitMask32(0))
		self.wsnp.node().setFromCollideMask(CIGlobals.EventBitmask)
			
		event = CollisionHandlerEvent()
		event.setInPattern("%fn-into")
		event.setOutPattern("%fn-out")
		base.cTrav.addCollider(self.wsnp, event)
		
	def throwObject(self, task):
		self.playWeaponSound()
		
		self.weaponNP = NodePath("weaponNP")
		self.weaponNP.setScale(render, 1)
		try: self.weaponNP.reparentTo(self.find('**/joint_nameTag'))
		except: return task.done
		self.weaponNP.setPos(0, 50, 0)
		self.weaponNP.setHpr(0, 0, 0)
		
		if self.weapon:
			self.weapon.setScale(self.weapon.getScale(render))
		try: self.weapon.reparentTo(render)
		except: return task.done
		
		self.weapon.setPos(0,0,0)
		self.weapon.setHpr(0,0,0)
		
		if self.attack == "glowerpower":
			self.weapon.setH(self.weaponNP.getH(render))
			self.wtrajectory = self.weapon.posInterval(0.5,
										Point3(self.weaponNP.getPos(render)),
										startPos=(self.getX(render), self.getY(render) + 3, self.find('**/joint_head').getZ(render)))
			self.wtrajectory.start()
		else:
			self.wtrajectory = ProjectileInterval(self.weapon,
										startPos = (self.suit.find('**/joint_Rhold').getPos(render)),
										endPos = self.weaponNP.getPos(render),
										gravityMult = 0.7, duration = 1)
			self.wtrajectory.start()
		if self.attack == "glowerpower":
			taskMgr.doMethodLater(0.5, self.delWeapon, "delWeapon")
		else:
			taskMgr.doMethodLater(1, self.delWeapon, "delWeapon")
		self.weapon_state = 'released'
		
	def playWeaponSound(self):
		if self.attack == "glowerpower":
			self.weapon_sfx = audio3d.loadSfx("phase_5/audio/sfx/SA_glower_power.ogg")
		elif self.attack == "canned":
			self.weapon_sfx = audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.ogg")
		elif self.attack == "clipontie":
			self.weapon_sfx = audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.ogg")
		elif self.attack == "sacked":
			self.weapon_sfx = audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.ogg")
		elif self.attack == "playhardball":
			self.weapon_sfx = audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.ogg")
		elif self.attack == "marketcrash":
			self.weapon_sfx = audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.ogg")
		if self.weapon:
			audio3d.attachSoundToObject(self.weapon_sfx, self.weapon)
			self.weapon_sfx.play()
			
	def exitAttack(self):
		pass
		
	def enterPie(self):
		self.suit.play("pie")
		
	def exitPie(self):
		self.exitGeneral()
		
	def enterWin(self):
		self.suit.play("win")
		
	def exitWin(self):
		self.exitGeneral()
			
	

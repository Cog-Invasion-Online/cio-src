"""
  
  Filename: DistributedSuit.py
  Created by: blach (??June14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.online.OnlineGlobals import *
from direct.interval.ProjectileInterval import ProjectileInterval
from lib.coginvasion.toon.ChatBalloon import ChatBalloon
from lib.coginvasion.toon.LabelScaler import LabelScaler
from lib.coginvasion.suit import Suit
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.showbase.ShadowPlacer import ShadowPlacer
from lib.coginvasion.toon import ParticleLoader
from direct.showbase.DirectObject import *
from direct.actor.Actor import *
from direct.gui.DirectGui import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.showbase import Audio3DManager
import random

notify = DirectNotify().newCategory("DistributedSuit")

audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
audio3d.setDistanceFactor(25)

class DistributedSuit(Suit.Suit, DistributedSmoothNode):
	
	def __init__(self, cr):
		try:
			self.DistributedSuit_initialized
			return
		except:
			self.DistributedSuit_initialized = 1
		Suit.Suit.__init__(self)
		DistributedSmoothNode.__init__(self, cr)
		self.name = ""
		self.anim = "neutral"
		self.state = "alive"
		self.damage = 0
		self.health = 132
		self.type = "A"
		self.team = "c"
		self.head = "bigcheese"
		self.name = "The Big Cheese"
		self.skeleton = 0
		self.dmg_lbl = None
		self.lbl_int = None
		self.bean = None
		return

	def setSuit(self, type, head, team, skeleton):
		self.type = type
		self.head = head
		self.team = team
		self.skeleton = skeleton
		self.health = CIGlobals.SuitHealthAmounts[head]
		Suit.Suit.generateSuit(self, type, head, team, self.health, skeleton)
		
	def b_setSuit(self, type, head, team, skeleton):
		self.d_setSuit(type, head, team, skeleton)
		self.setSuit(type, head, team, skeleton)
		
	def d_setSuit(self, type, head, team, skeleton):
		self.sendUpdate('setSuit', [type, head, team, skeleton])
		
	def deleteJellybean(self):
		self.deleteBean()
		
	def b_deleteJellybean(self):
		self.d_deleteJellybean()
		self.deleteJellybean()
		
	def d_deleteJellybean(self):
		self.sendUpdate("deleteJellybean", [])
		
	def addHealth(self, health):
		try:
			self.albl_int.pause()
			self.albl_int = None
			taskMgr.remove(self.taskName('delAddLbl'))
			self.add_lbl.remove()
			self.add_lbl = None
		except:
			pass
		self.admgTaskid = random.uniform(0, 203102301230)
		mf = loader.loadFont("phase_3/models/fonts/MickeyFont.bam")
		self.add_sfx = audio3d.loadSfx("phase_3/audio/sfx/health.ogg")
		audio3d.attachSoundToObject(self.add_sfx, self.suit)
		self.add_sfx.play()
		self.add_lbl = DirectLabel(text="+" + str(health), relief=None, text_align=TextNode.ACenter, parent=self.suit.find('**/joint_nameTag'), text_decal = True, scale=1.5, text_fg=(0, 1, 0, 1), pos=(0, 0, 3), text_font=mf)
		self.add_lbl.setBillboardPointEye()
		self.albl_int = self.add_lbl.posInterval(0.5, 
										Point3(self.tag.getPos() + (0, 0, 0.55)),
										startPos=(0, 0, 4), blendType='easeOut')
		self.albl_int.start()
		taskMgr.doMethodLater(2, self.delAddLbl, self.taskName('delAddLbl'))
		self.b_setHealth(self.getHealth() + health)
	
	def delAddLbl(self, task):
		try:
			self.add_lbl.remove()
			self.add_lbl = None
		except:
			pass
		return task.done
		
	def b_addHealth(self, health):
		self.d_addHealth(health)
		self.addHealth(health)
		
	def d_addHealth(self, health):
		self.sendUpdate('addHealth', [health])
		
	def setName(self, name):
		self.name = name
		Suit.Suit.setName(self, name, self.head)
	
	def b_setName(self, name):
		self.d_setName(name)
		self.setName(name)
	
	def d_setName(self, name):
		self.sendUpdate("setName", [name])
		
	def setChat(self, chat):
		self.chat = chat
		Suit.Suit.setChat(self, chat)
	
	def b_setChat(self, chat):
		self.d_setChat(chat)
		self.setChat(chat)
	
	def d_setChat(self, chat):
		self.sendUpdate("setChat", [chat])
		
	def createJellyBean(self):
		Suit.Suit.createJellyBean(self)
		
	def b_createJellyBean(self):
		self.d_createJellyBean()
		self.createJellyBean()
		
	def d_createJellyBean(self):
		self.sendUpdate("createJellyBean", [])
		
	def isDead(self):
		if self.health <= 0:
			return True
		else:
			return False
			
	def setDamage(self, damage):
		self.damage = damage
		try:
			self.lbl_int.pause()
			self.lbl_int = None
			taskMgr.remove("delLbl" + str(self.dmgTaskid))
			self.dmg_lbl.remove()
			self.dmg_lbl = None
		except:
			pass
		self.dmgTaskid = random.uniform(0, 203102301230)
		mf = loader.loadFont("phase_3/models/fonts/MickeyFont.bam")
		self.dmg_lbl = DirectLabel(text="-" + str(damage), relief=None, text_align=TextNode.ACenter, parent=self.suit.find('**/joint_nameTag'), text_decal = True, scale=1.5, text_fg=(0.9,0,0,1), pos=(0, 0, 3), text_font=mf)
		self.dmg_lbl.setBillboardPointEye()
		self.lbl_int = self.dmg_lbl.posInterval(0.5, 
										Point3(self.tag.getPos() + (0, 0, 0.55)),
										startPos=(0, 0, 4), blendType='easeOut')
		self.lbl_int.start()
		taskMgr.doMethodLater(2, self.delLbl, "delLbl" + str(self.dmgTaskid))
		self.b_setHealth(self.getHealth() - damage)
	
	def delLbl(self, task):
		try:
			self.dmg_lbl.remove()
			self.dmg_lbl = None
		except:
			pass
		return task.done
	
	def b_setDamage(self, damage):
		self.d_setDamage(damage)
		self.setDamage(damage)
	
	def d_setDamage(self, damage):
		self.sendUpdate("setDamage", [damage])
		
	def setHealth(self, health):
		self.health = health
		Suit.Suit.updateHealthBar(self, self.health)
	
	def b_setHealth(self, health):
		self.d_setHealth(health)
		self.setHealth(health)
	
	def d_setHealth(self, health):
		self.sendUpdate("setHealth", [health])
		
	def setAttack(self, attack):
		self.attack = attack
		
		self.animFSM.request('attack', enterArgList=[attack])
		Sequence(Wait(CIGlobals.SuitTimeUntilToss[attack][self.type]),
							Func(self.acceptWeaponCollisions)).start()
	
	def acceptWeaponCollisions(self):
		base.acceptOnce("weaponSensor" + str(self.weaponSensorId) + "-into", self.handleWeaponCollisions)
		
	def handleWeaponCollisions(self, entry):
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			if val.__class__.__name__ == "DistributedToonAI":
				if val.getPlace() == CIGlobals.ToontownCentral:
					if val.getKey() == toonNP.getKey():
						val.b_setDamage(self.damageAmount)
						Sequence(Wait(0.1), Func(self.checkToonHealth, val)).start()
			elif val.__class__.__name__ == "DistributedSuitAI":
				if val.getKey() == toonNP.getKey():
					if not val.getHealth() <= 0:
						val.b_addHealth(self.damageAmount)
		self.b_handleWeaponTouch()
		
	def checkToonHealth(self, obj):
		if obj.getHealth() >= 0:
			self.d_victory()
		
	def d_victory(self):
		self.sendUpdate("victory", [])
	
	def b_setAttack(self, attack):
		self.d_setAttack(attack)
		self.setAttack(attack)
	
	def d_setAttack(self, attack):
		self.sendUpdate("setAttack", [attack])
		
	def handleWeaponTouch(self):
		Suit.Suit.handleWeaponTouch(self)
	
	def b_handleWeaponTouch(self):
		self.d_handleWeaponTouch()
		self.handleWeaponTouch()
	
	def d_handleWeaponTouch(self):
		self.sendUpdate("handleWeaponTouch", [])
		
	def interruptAttack(self):
		Suit.Suit.interruptAttack(self)
		
	def b_interruptAttack(self):
		self.d_interruptAttack()
		self.interruptAttack()
		
	def d_interruptAttack(self):
		self.sendUpdate("interruptAttack", [])
	
	def suitLose(self):
		self.animFSM.request('die')
	
	def b_suitLose(self):
		self.d_suitLose()
		self.suitLose()
	
	def d_suitLose(self):
		self.sendUpdate("suitLose", [])
	
	def setAnimState(self, anim):
		self.anim = anim
		if self.suit is None:
			return
		self.animFSM.request(anim)
	
	def b_setAnimState(self, anim):
		self.d_setAnimState(anim)
		self.setAnimState(anim)
	
	def d_setAnimState(self, anim):
		self.sendUpdate("setAnimState", [anim])
		
	def flyDown(self):
		self.animFSM.request('flydown')
	
	def b_flyDown(self):
		self.d_flyDown()
		self.flyDown()
	
	def d_flyDown(self):
		self.sendUpdate("flyDown", [])
		
	def flyAway(self):
		self.animFSM.request('flyaway')
	
	def b_flyAway(self):
		self.d_flyAway()
		self.flyAway()
	
	def d_flyAway(self):
		self.sendUpdate("flyAway", [])
		
	def __showAvId(self):
		self.setDisplayName(self.getName() + "\n[" + str(self.doId) + "]")
		
	def __showName(self):
		self.setDisplayName(self.getName())
		
	def setDisplayName(self, name):
		Suit.Suit.setName(self, name, self.head)

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
		Suit.Suit.delete(self)
		DistributedSmoothNode.delete(self)
		

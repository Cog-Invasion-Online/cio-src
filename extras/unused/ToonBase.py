"""
  
  Filename: ToonBase.py
  Created by: blach (17June14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.online.OnlineGlobals import *
from lib.coginvasion.book.ShtickerBook import ShtickerBook
from lib.coginvasion.hood.HoodUtil import HoodUtil
from direct.controls import ControlManager
from direct.controls.GhostWalker import GhostWalker
from direct.controls.GravityWalker import GravityWalker
from direct.controls.ObserverWalker import ObserverWalker
from direct.controls.PhysicsWalker import PhysicsWalker
from direct.controls.SwimWalker import SwimWalker
from direct.controls.TwoDWalker import TwoDWalker
from direct.distributed.PyDatagram import PyDatagram
from lib.coginvasion.gui.LaffOMeter import LaffOMeter
from panda3d.core import *
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.actor.Actor import *
import SmartCamera
import random
import math
from lib.coginvasion.gui import PieGui
from lib.coginvasion.gui import GagShop
from lib.coginvasion.gui import MoneyGui
from lib.coginvasion.gui import ChatInput
from direct.interval.IntervalGlobal import *

notify = DirectNotify().newCategory("ToonBase")

WANTS_SUIT_INFO = 25004
SUIT_DOID = 25000
WANTS_BOSS_INFO = 25010
TROLLEY_REQ_ENTER = 420000
GAG_SHOP_EXIT = 7002
Y_FACTOR = -0.15
STATION_ABORT = 903

class ToonBase:

	def __init__(self, cr, head, headtype, headcolor, torsocolor, legcolor,
				gender, torsotype, legtype, name, shirtcolor, shortscolor, shirt, short, sleeve):
		self.cr = cr
		self.head = head
		self.headtype = headtype
		self.hr, self.hg, self.hb, self.ha = headcolor
		self.tr, self.tg, self.tb, self.ta = torsocolor
		self.lr, self.lg, self.lb, self.la = legcolor
		self.shir, self.shig, self.shib, self.shia = shirtcolor
		self.shor, self.shog, self.shob, self.shoa = shortscolor
		self.shirt = shirt
		self.short = short
		self.sleeve = sleeve
		self.gender = gender
		self.torsotype = torsotype
		self.legtype = legtype
		self.name = name
		
		base.avatar = None
		self.sb = ShtickerBook(self)
		
		self.laffMeter = LaffOMeter()
		
		self.run_sfx = loader.loadSfx("phase_3.5/audio/sfx/AV_footstep_runloop.ogg")
		self.run_sfx.setLoop(True)
		self.walk_sfx = loader.loadSfx("phase_3.5/audio/sfx/AV_footstep_walkloop.ogg")
		self.walk_sfx.setLoop(True)
		
		self.hoodUtil = HoodUtil(self.cr)
		
		self.smart_cam = SmartCamera.SmartCamera()
		
		self.isThrowing = False
		
		self.controlManager = ControlManager.ControlManager(True, False)
		
		self.offset = 3.2375
		
		self.keyMap = {"forward":0,"backward":0, "left":0, "right":0, "jump":0}
		
		base.cTrav = CollisionTraverser('general_traverser')
		self.dFov = CIGlobals.DefaultCameraFov
		self.oFov = CIGlobals.OriginalCameraFov
		
		self.createReady()
			
	def createReady(self):
		base.avatar = self.cr.createDistributedObject(className="DistributedToon", zoneId=5)
		base.avatar.b_setToon(self.gender, self.headtype, self.head, self.legtype, self.torsotype, self.hr, self.hg, self.hb, self.tr, self.tg,
						self.tb, self.lr, self.lg, self.lb, self.shir, self.shig, self.shib, self.shor,	self.shog, self.shob, self.shirt,
						self.short, self.sleeve)
		#base.avatar.initializeLocalSensor(2, 3, "localAvatar")
		base.avatar.initCollisions()
		#base.avatar.startBlink()
		base.avatar.startLookAround()
		base.avatar.startPosHprBroadcast()
		base.avatar.setMoney(20)
		base.accept("loadedHood", self.enterTeleportIn)
		base.accept("gotLookSpot", self.handleLookSpot)
		#base.accept("alt-1", self.enterFirstPerson)
		#base.accept("alt-2", self.exitFirstPerson)
		self.sendSuitInfoRequest()
		self.sendBossInfoRequest()
		self.setAvatarName(self.name)
		taskMgr.add(self.checkHealth, "checkHealth")
		self.smart_cam.set_default_pos(0.0, math.sqrt(base.avatar.getPart('head').getZ(base.avatar)) / Y_FACTOR, 
									base.avatar.getPart('head').getZ(base.avatar) + 0.3)
		self.smart_cam.set_parent(base.avatar)
		self.smart_cam.initialize_smartcamera()
		self.smart_cam.initialize_smartcamera_collisions()
		self.initMovement()
		self.pieGui = PieGui.PieGui(base.avatar.pies)
		self.pieGui.createGui()
		self.pieGui.enableWeaponSwitch()
		self.moneyGui = MoneyGui.MoneyGui()
		self.moneyGui.createGui()
		self.moneyGui.update()
		self.gagShop = GagShop.GagShop()
		self.changeHood(10, base.avatar.zoneId)
		base.camLens.setMinFov(self.dFov/(4./3.))
		base.accept("SuitsActive", self.handleSuitsActive)
		base.accept("SuitsInactive", self.handleSuitsInactive)
		base.accept("fullTrolley", self.handleFullTrolley)
		base.accept("openTrolley", self.handleOpenTrolley)
		base.accept("tookDamage", self.handleTookDamage)
		base.accept("enterGagShop", self.enterGagShop)
		base.accept("exitGagShop", self.exitGagShop)
		base.accept("moneyChanged", self.moneyGui.update)
		base.accept("ammoChanged", self.pieGui.update)
		base.accept("collectedMoney", self.handleMoneyCollected)
		base.accept("restartGame", self.exitGame)
		base.accept("bossSpawned", self.handleBossSpawned)
		base.accept("lostConnection", self.delete)
		base.accept("MinigameStationSlotOpen", self.handleMinigameStationSlotOpen)
		base.accept("MinigameStationHeadOff", self.handleMinigameStationHeadOff)
		self.createGui()
		
	def enterFirstPerson(self):
		base.avatar.toon_head.hide()
		base.camLens.setMinFov(70.0 / (4./3.))
		base.avatar.deleteShadow()
		self.smart_cam.enterFirstPerson()
		
	def exitFirstPerson(self):
		base.avatar.toon_head.show()
		base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
		base.avatar.initShadow(base.avatar.avatarType)
		self.smart_cam.exitFirstPerson()
		
	def delete(self):
		self.cr.getCurrentHood().unloadHood()
		self.pieGui.deleteGui()
		self.moneyGui.deleteGui()
		self.smart_cam.stop_smartcamera()
		self.chatInput.delete()
		self.disableMovement()
		base.avatar.stopLookAround()
		base.avatar.stopBlink()
		base.avatar.sendDeleteMsg()
		self.deleteLaffMeter()
		self.book_btn.destroy()
		self.book_gui.removeNode()
		base.ignore("exitGagShop")
		base.ignore("moneyChanged")
		base.ignore("ammoChanged")
		base.ignore("collectedMoney")
		base.ignore("restartGame")
		base.ignore("SuitsActive")
		base.ignore("SuitsInactive")
		base.ignore("fullTrolley")
		base.ignore("openTrolley")
		base.ignore("tookDamage")
		base.ignore("enterGagShop")
		base.ignore("loadedHood")
		base.ignore("gotLookSpot")
		base.ignore("bossSpawned")
		base.ignore("lostConnection")
		#base.ignore("alt-1")
		#base.ignore("alt-2")
		base.ignore("MinigameStationSlotOpen")
		base.ignore("MinigameStationHeadOff")
		taskMgr.remove("checkHealth")
		base.camLens.setMinFov(self.oFov/(4./3.))
		camera.reparentTo(render)
		camera.setPos(0,0,0)
		camera.setHpr(0,0,0)
		del base.avatar
		del self.laffMeter
		del self.pieGui
		del self.sb
		del self.smart_cam
		del self.controlManager
		del self.walkControls
		del self.hoodUtil
		del self.cr
		del self.head
		del self.headtype
		del self.hr, self.hg, self.hb, self.ha
		del self.tr, self.tg, self.tb, self.ta
		del self.lr, self.lg, self.lb, self.la
		del self.gender
		del self.torsotype
		del self.legtype
		del self.shir, self.shig, self.shib
		del self.shor, self.shog, self.shob
		del self.sleeve, self.shirt, self.short
		del self.name
		del self.keyMap
		del self.offset
		if hasattr(self, 'dmg2BeDone'):
			del self.dmg2BeDone
		del self.run_sfx
		del self.walk_sfx
		del self.isThrowing
		del self.book_btn
		del self.book_gui
		del self.chatInput
		return
	
	def handleBossSpawned(self):
		if base.avatar.zoneId == 20:
			self.hoodUtil.centralHood.bossSpawned()
			
	def handleMinigameStationSlotOpen(self, slot, sdoid, adoid):
		if adoid == base.avatar.doId:
			for key in self.cr.doId2do.keys():
				station = self.cr.doId2do[key]
				if station.__class__.__name__ == "DistributedMinigameStation":
					if station.doId == sdoid:
						if slot == 1:
							self.enterMinigameStationSlot(station.circle1, station)
						elif slot == 2:
							self.enterMinigameStationSlot(station.circle2, station)
						elif slot == 3:
							self.enterMinigameStationSlot(station.circle3, station)
					
	def enterMinigameStationSlot(self, circle, station):
		self.disableMovement()
		self.smart_cam.stop_smartcamera()
		camera.reparentTo(station)
		camera.setPos(0, 30.0, 22.5)
		camera.setPos(camera.getPos(render))
		camera.reparentTo(render)
		camera.lookAt(station.sign)
		self.book_btn.hide()
		base.avatar.headsUp(circle)
		base.avatar.b_setAnimState("run")
		runTrack = LerpPosInterval(base.avatar,
								1.0,
								circle.getPos(render),
								startPos=base.avatar.getPos(render))
		runTrack.start()
		Sequence(Wait(1), Func(self.createStationAbortGui), Func(base.avatar.b_setAnimState, "neutral"), Func(base.avatar.headsUp, station.sign)).start()
		
	def createStationAbortGui(self):
		qt_btn = loader.loadModel("phase_3/models/gui/quit_button.bam")
		self.abortBtn = DirectButton(text="Abort", geom=(qt_btn.find('**/QuitBtn_UP'),
											qt_btn.find('**/QuitBtn_DN'),
											qt_btn.find('**/QuitBtn_RLVR')), relief=None, scale=1.2, text_scale=0.055,
											pos=(0, 0, 0.85), command=self.sendStationAbort)
											
	def sendStationAbort(self):
		self.abortBtn.destroy()
		del self.abortBtn
		pkg = PyDatagram()
		pkg.addUint16(STATION_ABORT)
		pkg.addUint32(base.avatar.doId)
		self.cr.send(pkg)
		self.abortStation()
		
	def abortStation(self):
		self.enableMovement()
		self.book_btn.show()
		self.startSmartCam()
		
	def handleMinigameStationHeadOff(self, game, doid, zone):
		if doid == base.avatar.doId:
			self.abortBtn.destroy()
			del self.abortBtn
			self.startSmartCam()
			self.enterTeleportOut(None)
			Sequence(Wait(6.0), Func(self.changeHood, zone, base.avatar.zoneId, place="minigame")).start()
		
	def startSmartCam(self):
		self.smart_cam.initialize_smartcamera()
		self.smart_cam.initialize_smartcamera_collisions()
		self.smart_cam.start_smartcamera()
		
	def resetSmartCam(self):
		self.smart_cam.stop_smartcamera()
		self.startSmartCam()
		
	def enterGagShop(self):
		self.disableMovement()
		self.gagShop.enter()
		
	def exitGagShop(self):
		self.enableMovement()
		pkg = PyDatagram()
		pkg.addUint16(GAG_SHOP_EXIT)
		self.cr.send(pkg)
		
	def handleMoneyCollected(self, money):
		base.avatar.setMoney(base.avatar.getMoney() + money)
		
	def createGui(self):
		if base.config.GetBool('want-chat', True):
			self.chatInput = ChatInput.ChatInput()
			self.chatInput.createGui()
			self.chatInput.enableKeyboardShortcuts()
		self.book_gui = loader.loadModel("phase_3.5/models/gui/sticker_open_close_gui.bam")
		self.book_btn = DirectButton(geom=(self.book_gui.find('**/BookIcon_CLSD'),
											self.book_gui.find('**/BookIcon_OPEN'),
											self.book_gui.find('**/BookIcon_RLVR')), relief=None, pos=(-0.175, 0, 0.163), command=self.startBook, scale=(0.7, 0.8, 0.8), parent=base.a2dBottomRight)
		self.book_btn.hide()
		
	def createLaffMeter(self):
		self.laffMeter.generate(base.avatar.hr, base.avatar.hg, base.avatar.hb, base.avatar.head)
		self.laffMeter.start()
		
	def deleteLaffMeter(self):
		self.laffMeter.destroy()

	def setAvatarName(self, name):
		base.avatar.b_setName(name)
		base.avatar.tag['text_fg'] = CIGlobals.LocalNameTagColor

	def initMovement(self):
		self.walkControls = GravityWalker(legacyLifter=True)
		self.walkControls.setWallBitMask(CIGlobals.WallBitmask)
		self.walkControls.setFloorBitMask(CIGlobals.FloorBitmask)
		self.walkControls.setWalkSpeed(30, 30, 15, 75)
		self.walkControls.initializeCollisions(base.cTrav, base.avatar, floorOffset=0.025, reach=4.0)
		self.walkControls.setAirborneHeightFunc(self.getAirborneHeight)
		camera.reparent_to(base.avatar)
		self.smart_cam.start_smartcamera()

	def getAirborneHeight(self):
		return self.offset + 0.025000000000000001

	def enableMovement(self):
		self.movementEnabled = True
		self.walkControls.enableAvatarControls()
		base.accept("arrow_up", self.setKey, ["forward",1])
		base.accept("arrow_up-up", self.setKey, ["forward",0])
		base.accept("arrow_down", self.setKey, ["backward",1])
		base.accept("arrow_down-up", self.setKey, ["backward",0])
		base.accept("arrow_left", self.setKey, ["left", 1])
		base.accept("arrow_left-up", self.setKey, ["left", 0])
		base.accept("arrow_right", self.setKey, ["right",1])
		base.accept("arrow_right-up", self.setKey, ["right",0])
		base.accept("control", self.setKey, ["jump",1])
		base.accept("control-up", self.setKey, ["jump", 0])
		if base.config.GetBool('want-weapons', True):
			if base.config.GetBool('want-pies', True):
				base.accept("delete", self.startPie)
				base.accept("delete-up", self.throwPie)
		
		base.avatar.b_setAnimState("neutral")
		
		self.isMoving_forward = True
		self.isMoving_side = True
		
		taskMgr.add(self.move, "movetask")
		
	def startPie(self):
		if not base.avatar.pies.getAmmo() <= 0:
			# We need to store the damage amount to be done
			# so the avatar can't switch weapons while
			# the pie is airborne to do more damage without
			# losing the ammo.
			self.dmg2BeDone = base.avatar.pies.getDamage()
			self.isThrowing = True
			self.resetHeadHpr()
			base.avatar.stopLookAround()
			base.avatar.b_pieStart()
			base.avatar.pies.pieCollisions()

	def throwPie(self):
		base.avatar.b_pieThrow()
		self.disableThrow()
		taskMgr.doMethodLater(0.75, self.releasePie, "releasePie")
		taskMgr.doMethodLater(1.05, self.enableThrow, "enablepie")
		
	def disableThrow(self):
		base.ignore("delete")
		base.ignore("delete-up")

	def releasePie(self, task):
		base.avatar.b_pieRelease()
		self.isThrowing = False
		base.acceptOnce("pieSensor-into", self.checkPieCollisions)
		return task.done

	def enableThrow(self, task):
		if base.avatar.isDead():
			return
		base.avatar.startLookAround()
		base.accept("delete", self.startPie)
		base.accept("delete-up", self.throwPie)
		return

	def checkPieCollisions(self, entry):
		"""This method will figure out which CollisionNode the pie hit.
		If the hit CollisionNode is a Suit, then we'll send a datagram of
		the Suit's DoId to all clients. The client will then decide if
		the DoId sent matches its local DoId. If true, the Suit will take
		damage."""
		
		if base.avatar.pies.pie_state == 'start':
			return
		intoNP = entry.getIntoNodePath()
		suitNP = intoNP.getParent()
		for key in self.cr.doId2do.keys():
			val = self.cr.doId2do[key]
			# Let's see if the DoId ties into a Suit class.
			if "Suit" in val.__class__.__name__:
				if val.getKey() == suitNP.getKey():
					# It's true! Let's send a datagram of the DoId over the network.
					if val.getHealth() > 0:
						val.b_setDamage(self.dmg2BeDone)
						taskMgr.doMethodLater(0.1, self.checkSuitHealth, "checkSuitHealth", extraArgs=[val], appendTask=True)
			elif val.__class__.__name__ == "DistributedToon":
				if val.getKey() == suitNP.getKey():
					if not val.isDead():
						if val.getHealth() < 50:
							val.b_addHealth(1)
		base.avatar.b_handlePieSplat()
		
	def checkSuitHealth(self, suit, task):
		money = int(suit.maxHP / CIGlobals.SuitAttackDamageFactors['clipontie'])
		if suit.getHealth() <= 0:
			base.avatar.setMoney(base.avatar.getMoney() + money)
		return task.done
		
	def nul(self):
		pass
		
	def handleLookSpot(self, hpr):
		h, p, r = hpr
		base.avatar.d_lookAtObject(h, p, r)
		
	def startBook(self):
		self.resetHeadHpr()
		base.avatar.stopLookAround()
		self.book_btn.remove()
		self.disableMovement()
		base.avatar.b_openBook()
		taskMgr.doMethodLater(0.5, self.idleBook, "idlebook")

	def idleBook(self, task):
		self.sb.createBG()
		self.sb.zonePage()
		base.avatar.b_readBook()
		self.book_btn = DirectButton(geom=(self.book_gui.find('**/BookIcon_OPEN'),
											self.book_gui.find('**/BookIcon_CLSD'),
											self.book_gui.find('**/BookIcon_RLVR2')), relief=None, pos=(-0.175, 0, 0.163), command=self.endBook, extraArgs=["closebook"], scale=(0.7, 0.8, 0.8), parent=base.a2dBottomRight)
		self.book_btn.setBin('gui-popup', 60)
		return task.done

	def endBook(self, direction):
		self.sb.closeBook()
		self.book_btn.hide()
		base.avatar.b_closeBook()
		taskMgr.doMethodLater(2, self.finishBook, "finishBook", extraArgs=[None, direction])
		
	def finishBook(self, task, direction):
		base.avatar.startLookAround()
		self.book_btn['geom'] = (self.book_gui.find('**/BookIcon_CLSD'), self.book_gui.find('**/BookIcon_OPEN'), self.book_gui.find('**/BookIcon_RLVR'))
		self.book_btn['command'] = self.startBook
		self.book_btn['extraArgs'] = []
		if direction == "closebook":
			self.enableMovement()
			self.book_btn.show()

	def enterTeleportOut(self, task, place="hood"):
		base.avatar.stopLookAround()
		self.resetHeadHpr()
		base.avatar.b_teleportOut()
		self.moneyGui.deleteGui()
		self.pieGui.deleteGui()
		self.laffMeter.disable()

	def enterTeleportIn(self, place="hood"):
		base.avatar.setPos(0,0,0)
		base.avatar.setHpr(0,0,0)
		if place == "hood":
			base.avatar.b_teleportIn()
			taskMgr.doMethodLater(1, self.enableMovementAfterTele, "emat")
			self.pieGui.createGui()
			self.moneyGui.createGui()
			self.createLaffMeter()
			self.resetSmartCam()
		elif place == "minigame":
			self.smart_cam.stop_smartcamera()
			camera.setPos(0,0,0)
			camera.setHpr(0,0,0)
			base.avatar.d_clearSmoothing()
			base.avatar.b_setAnimState("neutral")
			self.pieGui.deleteGui()
			self.moneyGui.deleteGui()
			self.book_btn.hide()

	def enableMovementAfterTele(self, task):
		base.avatar.startLookAround()
		base.avatar.b_setAnimState("neutral")
		self.enableMovement()
		self.book_btn.show()
		return task.done
		
	def changeHoodTask(self, task, newzoneid, currentzoneid):
		self.changeHood(newzoneid, currentzoneid)
		
	def changeHood(self, newzoneid, currentzoneid, place="hood"):
		if currentzoneid == 10:
			self.hoodUtil.unload("home")
		elif currentzoneid == 20:
			self.hoodUtil.unload("TT")
		elif currentzoneid == 30:
			self.hoodUtil.unload("minigamearea")
		if newzoneid == 10:
			self.cr.setObjectZone(base.avatar, 10)
			self.hoodUtil.load("home")
			base.avatar.b_setPlace(CIGlobals.Estate)
		elif newzoneid == 20:
			self.cr.setObjectZone(base.avatar, 20)
			self.hoodUtil.load("TT")
			base.avatar.b_setPlace(CIGlobals.ToontownCentral)
			if self.cr.SuitsActive == 1:
				self.hoodUtil.enableSuitEffect(self.cr.invasionSize)
				if self.cr.BossActive == 1:
					self.handleBossSpawned()
		elif newzoneid == 30:
			self.cr.setObjectZone(base.avatar, 30)
			self.hoodUtil.load("minigamearea")
			base.avatar.b_setPlace(CIGlobals.MinigameArea)
		elif newzoneid == "exit":
			self.exitGame()
		else:
			self.cr.setObjectZone(base.avatar, newzoneid)
			messenger.send("loadedHood", [place])
		if newzoneid != "exit":
			self.spawn()
		
	def spawn(self):
		h = random.randint(0, 360)
		if base.avatar.zoneId == 20:
			point = random.randint(0, len(CIGlobals.SuitPaths) - 1)
			pos = CIGlobals.SuitPaths[point]
			base.avatar.setPos(pos)
		base.avatar.setH(h)
			
	def checkHealth(self, task):
		if base.avatar.getHealth() <= 0:
			base.avatar.b_toonLose()
			self.toonLose()
			return task.done
		return task.cont
		
	def exitGame(self):
		self.delete()
		messenger.send("enterPickAToon", [1])
		
	def toonLose(self):
		self.smart_cam.stop_smartcamera()
		self.disableMovement()
		aspect2d.hide()
		render2d.hide()
		camera.setPos(camera.getPos(render))
		camera.setHpr(camera.getHpr(render))
		camera.reparentTo(render)
		taskMgr.doMethodLater(8, self.leaveGame, "leaveGame")
		
	def leaveGame(self, task):
		self.delete()
		messenger.send("died")
		return task.done
		
	def handleSuitsActive(self, size):
		if base.avatar.zoneId == 20:
			self.hoodUtil.enableSuitEffect(size)
			
	def handleSuitsInactive(self):
		if base.avatar.zoneId == 20:
			self.hoodUtil.disableSuitEffect()
			
	def handleFullTrolley(self):
		notify.warning("Cannot enter full trolley!")

	def handleOpenTrolley(self):
		notify.info("Trolley is open!")
			
	def sendSuitInfoRequest(self):
		""" We have just arrived in-game, let's
		see if there are any active Suits. """
		
		pkg = PyDatagram()
		pkg.addUint16(WANTS_SUIT_INFO)
		self.cr.send(pkg)
		
	def sendBossInfoRequest(self):
		pkg = PyDatagram()
		pkg.addUint16(WANTS_BOSS_INFO)
		self.cr.send(pkg)
		
	def handleTrolleyEnter(self, entry):
		# Let's find out if we can join the trolley.
		pkg = PyDatagram()
		pkg.addUint16(TROLLEY_REQ_ENTER)
		self.cr.send(pkg)

	def handleTrolleyResponse(self):
		notify.info("Got response from trolley.")
		
	def resetHeadHpr(self):
		base.avatar.b_lookAtObject(0, 0, 0, blink=0)
		
	def handleTookDamage(self):
		if base.avatar.isDead():
			return
		base.avatar.stopLookAround()
		self.resetHeadHpr()
		self.disableMovement()
		if not base.avatar.isDead():
			taskMgr.doMethodLater(3, self.enableMovementTask, "enableMovementTask")
			
	def interruptPie(self):
		self.isThrowing = False
		self.cleanupPieModel()
		taskMgr.remove("releasePie")
		
	def cleanupPieModel(self):
		base.avatar.b_deletePie()
			
	def enableMovementTask(self, task):
		if base.avatar.isDead():
			return task.done
		base.avatar.startLookAround()
		self.enableMovement()
		return task.done
		
	def disableMovement(self):
		self.movementEnabled = False
		self.walkControls.disableAvatarControls()
		self.run_sfx.stop()
		self.walk_sfx.stop()
		base.ignore("arrow_up")
		base.ignore("arrow_up-up")
		base.ignore("arrow_down")
		base.ignore("arrow_down-up")
		base.ignore("arrow_left")
		base.ignore("arrow_left-up")
		base.ignore("arrow_right")
		base.ignore("arrow_right-up")
		base.ignore("control")
		base.ignore("control-up")
		base.ignore("delete")
		base.ignore("delete-up")
		
		self.isMoving_forward = True
		self.isMoving_side = True
		
	def setKey(self, key, value):
		self.keyMap[key] = value
		
	def move(self, task):
		if not self.movementEnabled:
			return task.done

		def checkIsAirborne(task):
			if not self.walkControls.isAirborne:
				if self.keyMap["forward"]!=0:
					if self.isMoving_forward is True:
						self.run_sfx.play()
						self.walk_sfx.stop()
						base.avatar.b_setAnimState("run")
						self.isMoving_forward = False
				elif (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0) or (self.keyMap["backward"]!=0):
					if self.isMoving_side is True:
						self.walk_sfx.play()
						self.run_sfx.stop()
						base.avatar.b_setAnimState("walk")
						self.isMoving_side = False
				else:
					base.avatar.b_setAnimState("neutral")
					self.isMoving_side = False
					self.isMoving_forward = False
				return task.done
			return task.cont

		if (self.keyMap["jump"]!=0):
			if self.isMoving_forward is False and self.isMoving_side is False:
				if not self.walkControls.isAirborne:
					if self.isThrowing:
						self.interruptPie()
					self.walk_sfx.stop()
					self.run_sfx.stop()
					base.avatar.b_setAnimState("jump")
					taskMgr.doMethodLater(0.01, checkIsAirborne, "checkisairborne")
			elif self.isMoving_forward is True or self.isMoving_side is True:
				if not self.walkControls.isAirborne:
					if self.isThrowing:
						self.interruptPie()
					self.walk_sfx.stop()
					self.run_sfx.stop()
					base.avatar.b_setAnimState("leap")
					taskMgr.doMethodLater(0.01, checkIsAirborne, "checkisairborne")

		elif (self.keyMap["forward"]!=0):
			if self.isMoving_forward is False:
				if not self.walkControls.isAirborne:
					if self.isThrowing:
						self.interruptPie()
					self.run_sfx.play()
					self.walk_sfx.stop()
					self.isMoving_side = False
					base.avatar.b_setAnimState("run")
					base.avatar.stopLookAround()
					self.resetHeadHpr()
					self.isMoving_forward = True

		elif (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0) or (self.keyMap["backward"]!=0):
			if self.isMoving_side is False:
				if not self.walkControls.isAirborne:
					if self.isThrowing:
						self.interruptPie()
					self.run_sfx.stop()
					self.walk_sfx.play()
					self.isMoving_forward = False
					base.avatar.stopLookAround()
					self.resetHeadHpr()
					base.avatar.setPlayRate(1.0, "walk")
					if self.keyMap["backward"] != 0 and self.keyMap["right"] == 0 and self.keyMap["left"] == 0:
						base.avatar.setPlayRate(-1.0, "walk")
					base.avatar.b_setAnimState("walk")
					self.isMoving_side = True

		else:
			if self.isMoving_forward or self.isMoving_side:
				if not self.walkControls.isAirborne:
					self.run_sfx.stop()
					self.walk_sfx.stop()
					base.avatar.b_setAnimState("neutral")
					base.avatar.startLookAround()
					self.resetHeadHpr()
					self.isMoving_side = False
					self.isMoving_forward = False
		
		return task.cont

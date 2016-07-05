# Filename: DistributedPieTurret.py
# Created by:  blach (14Jun15)

from panda3d.core import Point3, Vec3, Vec4, VBase4, CollisionNode, CollisionSphere, CollisionHandlerEvent

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func, LerpQuatInterval, Parallel, LerpScaleInterval, LerpColorScaleInterval, ActorInterval
from direct.distributed.ClockDelta import globalClockDelta
from direct.actor.Actor import Actor
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

import random

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCLookInterval
from lib.coginvasion.toon.ProjectilePie import ProjectilePie
from lib.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from lib.coginvasion.gags import GagGlobals

class DistributedPieTurret(DistributedAvatar, DistributedSmoothNode):
	notify = directNotify.newCategory("DistributedPieTurret")

	def __init__(self, cr):
		DistributedAvatar.__init__(self, cr)
		DistributedSmoothNode.__init__(self, cr)
		self.fsm = ClassicFSM(
			'DistributedPieTurret',
			[
				State('off', self.enterOff, self.exitOff),
				State('scan', self.enterScan, self.exitScan),
				#State('lockOn', self.enterLockOn, self.exitLockOn),
				State('shoot', self.enterShoot, self.exitShoot)
			],
			'off', 'off'
		)
		self.fsm.enterInitialState()
		self.cannon = None
		self.track = None
		self.avatar = None
		self.readyPie = None
		self.explosion = None
		self.wallCollNode = None
		self.eventCollNode = None
		self.event = None
		self.piesInFlight = []

	def setHealth(self, hp):
		DistributedAvatar.setHealth(self, hp)
		if self.getAvatar() == base.localAvatar.doId:
			base.localAvatar.getMyBattle().getTurretManager().updateTurretGui()

	def die(self):
		self.fsm.requestFinalState()
		turretPos = self.cannon.getPos(render)
		self.removeTurret()
		self.explosion = loader.loadModel("phase_3.5/models/props/explosion.bam")
		self.explosion.setScale(0.5)
		self.explosion.reparentTo(render)
		self.explosion.setBillboardPointEye()
		self.explosion.setPos(turretPos + (0, 0, 1))
		sfx = base.localAvatar.audio3d.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.mp3")
		base.localAvatar.audio3d.attachSoundToObject(sfx, self)
		base.playSfx(sfx)

	def showAndMoveHealthLabel(self):
		self.unstashHpLabel()
		self.stopMovingHealthLabel()
		moveTrack = LerpPosInterval(self.healthLabel,
								duration = 0.5,
								pos = Point3(0, 0, 5),
								startPos = Point3(0, 0, 0),
								blendType = 'easeOut')
		self.healthLabelTrack = Sequence(moveTrack, Wait(1.0), Func(self.stashHpLabel))
		self.healthLabelTrack.start()

	def enterOff(self):
		pass

	def exitOff(self):
		pass

	def makeSplat(self, pos):
		splat = Actor("phase_3.5/models/props/splat-mod.bam",
			{"chan": "phase_3.5/models/props/splat-chan.bam"})
		splat.setScale(0.5)
		splat.reparentTo(render)
		splat.setBillboardPointEye()
		splat.setColor(VBase4(1, 1, 0, 1))
		x, y, z = pos
		splat.setPos(x, y, z)
		sfx = base.localAvatar.audio3d.loadSfx("phase_4/audio/sfx/AA_wholepie_only.mp3")
		base.localAvatar.audio3d.attachSoundToObject(sfx, splat)
		base.playSfx(sfx)
		track = Sequence(
			ActorInterval(splat, "chan"),
			Func(splat.cleanup),
			Func(splat.removeNode)
		)
		track.start()

	def d_makeSplat(self, pos):
		self.sendUpdate("makeSplat", [pos])

	def b_makeSplat(self, pos):
		self.d_makeSplat(pos)
		self.makeSplat(pos)

	def shoot(self, suitId):
		self.fsm.request('shoot', [suitId])

	def enterShoot(self, suitId):
		if self.cannon:
			smoke = loader.loadModel("phase_4/models/props/test_clouds.bam")
			smoke.setBillboardPointEye()
			smoke.reparentTo(self.cannon.find('**/cannon'))
			smoke.setPos(0, 6, -3)
			smoke.setScale(0.5)
			smoke.wrtReparentTo(render)
			self.suit = self.cr.doId2do.get(suitId)
			self.cannon.find('**/cannon').lookAt(self.suit.find('**/joint_head'))
			self.cannon.find('**/square_drop_shadow').headsUp(self.suit.find('**/joint_head'))
			self.eventId = random.uniform(0, 100000000)
			track = Sequence(Parallel(LerpScaleInterval(smoke, 0.5, 3), LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.removeNode))
			track.start()
			self.createAndShootPie()

	def loadPieInTurret(self):
		if self.cannon:
			if self.readyPie:
				self.readyPie.removeNode()
				self.readyPie = None
			pie = loader.loadModel("phase_3.5/models/props/tart.bam")
			pie.reparentTo(self.cannon.find('**/cannon'))
			pie.setY(5.2)
			pie.setHpr(90, -90, 90)
			self.readyPie = pie

	def removePieInTurret(self):
		if self.readyPie:
			self.readyPie.removeNode()
			self.readyPie = None

	def createAndShootPie(self):
		if not self.readyPie:
			self.loadPieInTurret()
		local = 0
		if base.localAvatar.doId == self.getAvatar():
			local = 1
		proj = ProjectilePie(self.uniqueName('pieTurretCollision') + str(self.eventId), self.cannon.find('**/cannon'), self.readyPie, Point3(0, 200, -90), 0.9, 2.5, local, self)
		self.readyPie = None
		self.piesInFlight.append(proj)
		if local:
			self.acceptOnce(self.uniqueName('pieTurretCollision') + str(self.eventId), self.handlePieCollision)
		Sequence(Wait(0.25), Func(self.loadPieInTurret)).start()

	def handlePieCollision(self, entry, proj):
		x, y, z = proj.pie.getPos(render)
		self.b_makeSplat([x, y, z])
		proj.cleanup()
		if base.localAvatar.doId == self.getAvatar():
			intoNP = entry.getIntoNodePath()
			avNP = intoNP.getParent()
			for key in self.cr.doId2do.keys():
				obj = self.cr.doId2do[key]
				if obj.__class__.__name__ == "DistributedSuit":
					if obj.getKey() == avNP.getKey():
						if obj.getHealth() > 0:
							base.localAvatar.sendUpdate('suitHitByPie', [obj.doId, GagGlobals.getIDByName(CIGlobals.WholeCreamPie)])

	def exitShoot(self):
		del self.suit
		del self.eventId

	def scan(self, timestamp = None, afterShooting = 0):
		if timestamp == None:
			ts = 0.0
		else:
			ts = globalClockDelta.localElapsedTime(timestamp)

		self.fsm.request('scan', [ts, afterShooting])

	def enterScan(self, ts = 0, afterShooting = 0):
		if afterShooting:
			self.track = Parallel(
				LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
					startHpr = self.cannon.find('**/cannon').getHpr(), blendType = 'easeInOut'),
				LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
					startHpr = self.cannon.find('**/square_drop_shadow').getHpr(), blendType = 'easeInOut'),
				name = "afterShootTrack" + str(id(self))
			)
			self.track.setDoneEvent(self.track.getName())
			self.acceptOnce(self.track.getDoneEvent(), self._afterShootTrackDone)
			self.track.start(ts)
		else:
			self.track = Parallel(
				Sequence(
					LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (60, 0, 0),
						startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
					LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
						startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
				),
				Sequence(
					LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (60, 0, 0),
						startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
					LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
						startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
				)
			)
			self.track.loop(ts)

	def _afterShootTrackDone(self):
		self.track = None
		self.track = Parallel(
			Sequence(
				LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (60, 0, 0),
					startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
				LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
					startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
			),
			Sequence(
				LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (60, 0, 0),
					startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
				LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
					startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
			)
		)
		self.track.loop()

	def exitScan(self):
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None

	def setAvatar(self, avId):
		self.avatar = avId

	def getAvatar(self):
		return self.avatar

	def makeTurret(self):
		self.cannon = loader.loadModel("phase_4/models/minigames/toon_cannon.bam")
		self.cannon.reparentTo(self)
		self.loadPieInTurret()
		self.setupWallSphere()
		if self.getAvatar() == base.localAvatar.doId:
			self.setupEventSphere()

	def setupWallSphere(self):
		sphere = CollisionSphere(0.0, 0.0, 0.0, 3.0)
		node = CollisionNode('DistributedPieTurret.WallSphere')
		node.addSolid(sphere)
		node.setCollideMask(CIGlobals.WallBitmask)
		self.wallCollNode = self.cannon.attachNewNode(node)
		self.wallCollNode.setZ(2)
		self.wallCollNode.setY(1.0)

	def removeWallSphere(self):
		if self.wallCollNode:
			self.wallCollNode.removeNode()
			self.wallCollNode = None

	def removeTurret(self):
		self.removeWallSphere()
		self.removePieInTurret()
		if self.cannon:
			self.cannon.removeNode()
			self.cannon = None

	def generate(self):
		DistributedAvatar.generate(self)
		DistributedSmoothNode.generate(self)

	def announceGenerate(self):
		DistributedAvatar.announceGenerate(self)
		DistributedSmoothNode.announceGenerate(self)
		self.healthLabel.setScale(1.1)
		self.makeTurret()

	def disable(self):
		self.fsm.requestFinalState()
		del self.fsm
		for projs in self.piesInFlight:
			projs.cleanup()
		self.piesInFlight = None
		if self.explosion:
			self.explosion.removeNode()
			self.explosion = None
		self.removeTurret()
		DistributedSmoothNode.disable(self)
		DistributedAvatar.disable(self)

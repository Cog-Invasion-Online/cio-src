# Filename: ProjectilePie.py
# Created by:  blach (14Jun15)

from panda3d.core import CollisionNode, CollisionSphere, CollisionHandlerEvent, NodePath, BitMask32

from direct.interval.IntervalGlobal import ProjectileInterval
from direct.showbase.DirectObject import DirectObject

from lib.coginvasion.globals import CIGlobals

class ProjectilePie(DirectObject):

	def __init__(self, collideEventName, parent, pie, endPos, gravityMult, duration, local, turretClass):
		self.turret = turretClass
		self.collideEventName = collideEventName
		self.pieNp = NodePath('pieNP')
		self.pieNp.reparentTo(parent)
		self.pieNp.setScale(render, 1)
		self.pieNp.setPos(endPos)
		self.pieNp.setHpr(90, -90, 90)

		self.pie = pie
		if local:
			self.pieCollisions()
		self.pie.setScale(self.pie.getScale(render))
		self.pie.setPos(self.pie.getPos(render))
		self.pie.reparentTo(render)
		self.pie.setHpr(self.pieNp.getHpr(render))

		self.trajectory = ProjectileInterval(self.pie,
					startPos = self.pie.getPos(render),
					endPos = self.pieNp.getPos(render),
					gravityMult = gravityMult, duration = duration, name = 'projectilePieTraj' + str(id(self)))
		self.trajectory.setDoneEvent(self.trajectory.getName())
		self.acceptOnce(self.trajectory.getDoneEvent(), self.handleTrajDone)
		self.trajectory.start()
		sfx = base.localAvatar.audio3d.loadSfx("phase_4/audio/sfx/MG_cannon_fire_alt.mp3")
		base.localAvatar.audio3d.attachSoundToObject(sfx, parent)
		base.playSfx(sfx)

		if local:
			self.acceptOnce('projectilePieSensor' + str(id(self)) + '-into', self.handleCollision)

	def pieCollisions(self):
		pss = CollisionSphere(0,0,0,1)
		psnode = CollisionNode('projectilePieSensor' + str(id(self)))
		psnode.add_solid(pss)
		self.psnp = self.pie.attach_new_node(psnode)
		self.psnp.set_collide_mask(BitMask32(0))
		self.psnp.node().set_from_collide_mask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)

		event = CollisionHandlerEvent()
		event.set_in_pattern("%fn-into")
		event.set_out_pattern("%fn-out")
		base.cTrav.add_collider(self.psnp, event)

	def handleCollision(self, entry):
		messenger.send(self.collideEventName, [entry, self])

	def handleTrajDone(self):
		self.cleanup()

	def cleanup(self):
		self.ignore(self.trajectory.getDoneEvent())
		self.trajectory.finish()
		del self.trajectory
		if self.turret.piesInFlight:
			self.turret.piesInFlight.remove(self)
		self.ignore('projectilePieSensor' + str(id(self)) + '-into')
		del self.collideEventName
		if hasattr(self, 'psnp'):
			self.psnp.removeNode()
			del self.psnp
		self.pie.removeNode()
		del self.pie
		del self.pieNp
		del self.turret

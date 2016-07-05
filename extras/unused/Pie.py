"""

  Filename: Pie.py
  Created by: blach (17Mar15)

"""

from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.Audio3DManager import Audio3DManager
import random

if game.process == "client":
	audio3d = Audio3DManager(base.sfxManagerList[0], camera)
	audio3d.setDistanceFactor(25)

class Pie:
	notify = directNotify.newCategory("Pie")
	
	def __init__(self, pies, avatar, pie_type):
		self.pies = pies
		self.avatar = avatar
		self.pie = None
		self.pie_state = "start"
		self.pie_type = pie_type
		self.woosh = None
		self.trajectory = None
		self.pieNp = None
		self.psnp = None
		return
		
	def load(self):
		self.pie_state = "start"
		self.pie = loader.loadModel(self.pies.models[self.pie_type])
		self.pie.reparentTo(self.avatar.getPart('torso').find('**/def_joint_right_hold'))
		self.pieCollisions()
		
	def throw(self):
		if self.pie is None or self.pie.isEmpty():
			return
		self.woosh = audio3d.loadSfx("phase_3.5/audio/sfx/AA_pie_throw_only.ogg")
		audio3d.attachSoundToObject(self.woosh, self.pie)
		self.woosh.play()
		
		self.pieNp = NodePath("PieNp")
		self.pieNp.reparentTo(self.avatar)
		self.pieNp.setScale(render, 1.0)
		self.pieNp.setPos(0, 160, -90)
		self.pieNp.setHpr(90, -90, 90)
			
		self.trajectory = ProjectileInterval(self.pie,
									startPos = (self.avatar.getPart('torso').find('**/def_joint_right_hold').getPos(render)),
									endPos = self.pieNp.getPos(render),
									gravityMult = 0.9, duration = 3)
		self.pie.setHpr(self.pieNp.getHpr(render))
		self.trajectory.start()
		self.pie.reparentTo(render)
		self.pie_state = 'released'
		
	def pieCollisions(self):
		pss = CollisionSphere(0,0,0,1)
		random_sensorName = random.uniform(0, 10000000)
		psnode = CollisionNode('pieSensor' + str(random_sensorName))
		psnode.add_solid(pss)
		self.psnp = self.pie.attach_new_node(psnode)
		self.psnp.set_collide_mask(BitMask32(0))
		self.psnp.node().set_from_collide_mask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask | CIGlobals.EventBitmask)
			
		event = CollisionHandlerEvent()
		event.set_in_pattern("%fn-into")
		event.set_out_pattern("%fn-out")
		base.cTrav.add_collider(self.psnp, event)
	
	def handlePieCollisions(self, entry):
		if self.pie_state == 'start':
			return
		intoNP = entry.getIntoNodePath()
		avNP = intoNP.getParent()
		for key in base.cr.doId2do.keys():
			obj = base.cr.doId2do[key]
			if obj.__class__.__name__ == "DistributedSuit":
				if obj.getKey() == avNP.getKey():
					if obj.getHealth() > 0:
						self.avatar.sendUpdate('suitHitByPie', [obj.doId])
						Sequence(Wait(0.1), Func(self.avatar.checkSuitHealth, obj)).start()
			elif obj.__class__.__name__ == "DistributedToon":
				if obj.getKey() == avNP.getKey():
					if obj.getHealth() < obj.getMaxHealth() and not obj.isDead():
						self.avatar.sendUpdate('toonHitByPie', [obj.doId])
		self.avatar.b_pieSplat()

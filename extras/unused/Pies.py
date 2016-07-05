"""

  Filename: Pies.py
  Created by: blach (06Aug14)

"""

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from direct.directnotify.DirectNotify import *
from lib.coginvasion.globals import CIGlobals
from direct.actor.Actor import *
from direct.particles.ParticleEffect import ParticleEffect

if game.process == 'client':
	audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
	audio3d.setDistanceFactor(25)
	audio3d.setDropOffFactor(0.025)

class Pies:
	notify = DirectNotify().newCategory("Pies")

	def __init__(self):
		self.models = {1: "phase_3.5/models/props/tart.bam",
			0: "phase_5/models/props/birthday-cake-mod.bam",
			2: "phase_5/models/props/cream-pie-slice.bam"}
		self.hitsounds = {1: "phase_4/audio/sfx/AA_wholepie_only.mp3",
					0: "phase_4/audio/sfx/AA_wholepie_only.mp3",
					2: "phase_3.5/audio/sfx/AA_tart_only.mp3"}
		self.splatcolors = {1: VBase4(1, 1, 0, 1),
					0: VBase4(1, 0, 1, 1),
					2: VBase4(1, 1, 0, 1)}
		self.playrates = {1: 1.0,
					0: 1.0,
					2: 1.0,
					3: 1.0}
		self.damage = {1: 36,
				0: 75,
				2: 17,
				3: 180}
		self.health = {1: 5,
				0: 10,
				2: 2}
		self.max_ammo = {1: 7,
				0: 3,
				2: 15,
				3: 2}
		self.current_ammo = {1: 7,
					0: 3,
					2: 15,
					3: 0}
		self.weapon_id_2_weapon = {
			0: "cake",
			1: "tart",
			2: "slice",
			3: "tnt"
		}
		self.avatar = None
		self.splat = None
		self.pie = None
		self.tnt = None
		self.tntSparks = None
		self.tntTrajectory = None
		self.tntExplosion = None
		self.woosh = None
		self.dynamiteSfx = None
		self.pie_type = 1 # Default pie is the wholecream pie.
		self.pie_state = "start"
		self.tnt_state = "ready"
		return

	def getPieTypeName(self):
		return self.weapon_id_2_weapon.get(self.pie_type, None)

	def attachTNT(self):
		self.detachTNT()
		self.tnt = Actor("phase_5/models/props/tnt-mod.bam", {"chan": "phase_5/models/props/tnt-chan.bam"})
		self.tnt.reparentTo(self.avatar.find('**/def_joint_right_hold'))
		self.tntSparks = ParticleEffect()
		self.tntSparks.loadConfig("phase_5/etc/tnt.ptf")
		#self.tntSparks.start(parent = self.tnt.find('**/joint_attachEmitter'),
		#	renderParent = self.tnt.find('**/joint_attachEmitter'))

	def detachTNT(self):
		if self.tntTrajectory:
			self.tntTrajectory.pause()
			self.tntTrajectory = None
		if self.tnt is not None:
			self.tnt.cleanup()
			self.tnt = None
		if self.tntSparks is not None:
			self.tntSparks.cleanup()
			self.tntSparks = None

	def delete(self):
		self.avatar = None
		if self.splat is not None:
			self.splat.cleanup()
			self.splat = None
		self.detachTNT()
		self.tnt = None
		self.tnt_state = None
		self.tntSparks = None
		if self.tntExplosion:
			self.tntExplosion.cleanup()
			self.tntExplosion = None
		if self.dynamiteSfx:
			self.dynamiteSfx.stop()
			self.dynamiteSfx = None
		if self.pie is not None:
			self.deletePie()
		self.pie_type = None
		self.pie_state = None
		self.current_ammo = None
		self.max_ammo = None
		self.damage = None
		self.playrates = None
		self.splatcolors = None
		self.hitsounds = None
		self.models = None
		return

	def setAvatar(self, avatar):
		self.avatar = avatar

	def getAvatar(self):
		return self.avatar

	def setPieType(self, pietype):
		self.pie_type = pietype
		weaponType = None
		if pietype in [0, 1, 2]:
			weaponType = "pie"
		elif pietype == 3:
			weaponType = "tnt"
		if hasattr(self.avatar, 'setWeaponType'):
			self.avatar.setWeaponType(weaponType)

	def getPieType(self):
		return self.pie_type

	def setAmmo(self, ammo, pietype=None):
		if pietype is None:
			pietype = self.getPieType()
		self.current_ammo[pietype] = ammo

	def getAmmo(self, pietype=None):
		if pietype is None:
			pietype = self.getPieType()
		return self.current_ammo[pietype]

	def getDamage(self, weapon_id = None):
		if weapon_id is None:
			return self.damage[self.pie_type]
		else:
			return self.damage[weapon_id]

	def getHealth(self, weapon_id = None):
		if weapon_id is None:
			return self.health[self.pie_type]
		else:
			return self.health[weapon_id]

	def deletePie(self):
		try:
			self.trajectory.pause()
		except:
			pass
		if self.pie:
			self.pie.removeNode()
			self.pie = None

	def pieStart(self):
		try:
			audio3d.detachSound(self.woosh)
			self.trajectory.pause()
			self.pie.remove()
			self.pie = None
		except:
			pass
		self.pie_state = 'start'
		self.pie = loader.loadModel(self.models[self.pie_type])
		self.pie.reparentTo(self.avatar.getPart('torso').find('**/def_joint_right_hold'))

		self.avatar.setPlayRate(self.playrates[self.pie_type], "pie")
		self.avatar.play("pie", fromFrame=0, toFrame=45)

	def tntStart(self):
		self.avatar.play("toss", fromFrame = 22)
		self.tnt_state = "start"

	def tntRelease(self):
		if self.tnt is None:
			return

		tntNp = self.avatar.attachNewNode('tntNp')
		tntNp.setScale(render, 1.0)
		tntNp.setPos(0, 160, -120)
		tntNp.setHpr(0, 90, 0)

		self.tntTrajectory = ProjectileInterval(self.tnt,
									startPos = (self.avatar.getPart('torso').find('**/def_joint_right_hold').getPos(render)),
									endPos = tntNp.getPos(render),
									gravityMult = 0.9, duration = 3)
		self.tnt.setHpr(tntNp.getHpr(render))
		self.tntTrajectory.start()
		self.tnt.reparentTo(render)
		self.tnt_state = "released"
		self.setAmmo(self.getAmmo() - 1)

	def handleTntHitGround(self):
		if not self.tnt:
			return

		self.tntSparks.start(parent = self.tnt.find('**/joint_attachEmitter'),
			renderParent = self.tnt.find('**/joint_attachEmitter'))

		self.dynamiteSfx = audio3d.loadSfx("phase_5/audio/sfx/TL_dynamite.mp3")
		audio3d.attachSoundToObject(self.dynamiteSfx, self.tnt)
		self.dynamiteSfx.play()

		self.tnt.play("chan")

		if self.tntTrajectory:
			self.tntTrajectory.pause()
			self.tntTrajectory = None

	def tntExplode(self):
		if not self.tnt:
			return

		self.tntExplosion = Actor("phase_5/models/props/kapow-mod.bam", {"chan": "phase_5/models/props/kapow-chan.bam"})
		self.tntExplosion.reparentTo(render)
		self.tntExplosion.setBillboardPointEye()
		self.tntExplosion.setPos(self.tnt.getPos(render) + (0, 0, 4))
		self.tntExplosion.setScale(0.5)
		self.tntExplosion.play("chan")
		if self.dynamiteSfx:
			self.dynamiteSfx.stop()
			self.dynamiteSfx = None
		explosionSfx = audio3d.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.mp3")
		audio3d.attachSoundToObject(explosionSfx, self.tntExplosion)
		SoundInterval(explosionSfx).start()
		if self.tntSparks:
			self.tntSparks.cleanup()
			self.tntSparks = None
		if self.tnt:
			self.tnt.cleanup()
			self.tnt = None
		self.tnt_state = "ready"
		if self.getAmmo(3) > 0 and self.getPieType() == 3:
			self.attachTNT()
			if hasattr(self.avatar, "enablePieKeys"):
				# This must be the local avatar
				self.avatar.enablePieKeys()
		taskMgr.doMethodLater(0.5, self.delTntExplosion, "delTntExplosion")

	def delTntExplosion(self, task):
		if self.tntExplosion:
			self.tntExplosion.cleanup()
			self.tntExplosion = None
		return task.done

	def tntCollisions(self):
		if not self.tnt:
			return
		tss = CollisionSphere(0, 0, 0, 1)
		tsNode = CollisionNode('tntSensor')
		tsNode.add_solid(tss)
		self.tsNp = self.tnt.attach_new_node(tsNode)
		self.tsNp.set_scale(0.75, 0.8, 0.75)
		self.tsNp.set_pos(0.0, 0.1, 0.5)
		self.tsNp.set_collide_mask(BitMask32(0))
		self.tsNp.node().set_from_collide_mask(CIGlobals.FloorBitmask)

		event = CollisionHandlerEvent()
		event.set_in_pattern("%fn-into")
		event.set_out_pattern("%fn-out")
		base.cTrav.add_collider(self.tsNp, event)

	def setTntPos(self, pos):
		if self.tnt:
			self.tnt.setPos(pos)

	def pieCollisions(self):
		pss = CollisionSphere(0,0,0,1)
		psnode = CollisionNode('pieSensor')
		psnode.add_solid(pss)
		self.psnp = self.pie.attach_new_node(psnode)
		self.psnp.set_collide_mask(BitMask32(0))
		self.psnp.node().set_from_collide_mask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)

		event = CollisionHandlerEvent()
		event.set_in_pattern("%fn-into")
		event.set_out_pattern("%fn-out")
		base.cTrav.add_collider(self.psnp, event)

	def pieThrow(self):
		self.avatar.play("pie", fromFrame=45, toFrame=90)

	def pieRelease(self):
		if self.pie is None:
			return

		self.woosh = audio3d.loadSfx("phase_3.5/audio/sfx/AA_pie_throw_only.mp3")
		audio3d.attachSoundToObject(self.woosh, self.pie)
		self.woosh.play()

		self.pieNp = NodePath("PieNp")
		self.pieNp.reparentTo(self.avatar)
		self.pieNp.setScale(render, 1.0)
		self.pieNp.setPos(0, 160, -90)
		self.pieNp.setHpr(90, -90, 90)

		self.pie.setScale(self.pie.getScale(render))
		self.pie.reparentTo(render)
		self.pie.setHpr(self.pieNp.getHpr(render))

		self.trajectory = ProjectileInterval(self.pie,
									startPos = (self.avatar.getPart('torso').find('**/def_joint_right_hold').getPos(render)),
									endPos = self.pieNp.getPos(render),
									gravityMult = 0.9, duration = 3)
		self.trajectory.start()
		self.pie_state = 'released'
		self.setAmmo(self.getAmmo() - 1)

	def handlePieSplat(self):
		if self.splat:
			self.splat.cleanup()
			self.splat = None

		if self.pie_type == 3:
			# Not sure why I get a KeyError: 3 crash, but just for now
			# return if the pie type is tnt (3).
			return

		self.splat = Actor("phase_3.5/models/props/splat-mod.bam",
						{"chan": "phase_3.5/models/props/splat-chan.bam"})
		self.splat_sfx = audio3d.loadSfx(self.hitsounds[self.pie_type])
		audio3d.attachSoundToObject(self.splat_sfx, self.splat)
		self.splat_sfx.play()
		pietype2splatscale = {
			0: 0.6,
			1: 0.5,
			2: 0.35
		}
		self.splat.setScale(pietype2splatscale[self.pie_type])
		self.splat.reparentTo(render)
		self.splat.setBillboardPointEye()
		self.splat.setColor(self.splatcolors[self.pie_type])
		if self.pie and self.splat:
			self.splat.setPos(self.pie.getPos(render))
			self.splat.play("chan")

		if self.woosh:
			self.woosh.stop()
			self.woosh = None
		try:
			self.trajectory.pause()
		except:
			pass
		if self.pie:
			self.pie.removeNode()
			self.pie = None
		taskMgr.doMethodLater(0.5, self.delSplat, "delSplat")
		del pietype2splatscale

	def delSplat(self, task):
		if self.splat:
			self.splat.cleanup()
			self.splat = None
		return task.done

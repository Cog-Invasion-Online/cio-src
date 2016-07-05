"""
  
  Filename: NewPies.py
  Created by: blach (06Aug14)
  
"""

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from direct.directnotify.DirectNotify import *
from lib.coginvasion.globals import CIGlobals
from direct.actor.Actor import *
from Pie import Pie

if game.process == 'client':
	audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
	audio3d.setDistanceFactor(25)

class Pies:
	notify = DirectNotify().newCategory("Pies")
			
	def __init__(self):
		self.models = {1: "phase_3.5/models/props/tart.bam",
			0: "phase_5/models/props/birthday-cake-mod.bam",
			2: "phase_5/models/props/cream-pie-slice.bam"}
		self.hitsounds = {1: "phase_4/audio/sfx/AA_wholepie_only.ogg",
					0: "phase_4/audio/sfx/AA_wholepie_only.ogg",
					2: "phase_3.5/audio/sfx/AA_tart_only.ogg"}
		self.splatcolors = {1: VBase4(1, 1, 0, 1),
					0: VBase4(1, 0, 1, 1),
					2: VBase4(1, 1, 0, 1)}
		self.playrates = {1: 1.0,
					0: 1.0,
					2: 1.0}
		self.damage = {1: 36,
				0: 75,
				2: 17}
		self.max_ammo = {1: 7,
				0: 3,
				2: 15}
		self.current_ammo = {1: 7,
					0: 3,
					2: 15}
		self.avatar = None
		self.splat = None
		self.pie = None
		self.woosh = None
		self.pie_type = 1 # Default pie is the wholecream pie.
		self.pie_state = "start"
		return
		
	def delete(self):
		self.avatar = None
		if self.splat is not None:
			self.splat.cleanup()
			self.splat = None
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
		
	def getDamage(self):
		return self.damage[self.pie_type]
		
	def deletePie(self):
		try:
			self.trajectory.pause()
		except:
			pass
		if self.pie:
			self.pie.removeNode()
			self.pie = None
		
	def pieStart(self):
		self.pie = Pie(self, self.avatar, self.pie_type)
		self.pie.load()
		
		self.avatar.setPlayRate(self.playrates[self.pie_type], "pie")
		self.avatar.play("pie", fromFrame=0, toFrame=45)
		
	def pieThrow(self):
		self.avatar.play("pie", fromFrame=45, toFrame=90)
		
	def pieRelease(self):
		if self.pie is None:
			return
		self.pie.throw()
		self.setAmmo(self.getAmmo() - 1)
			
	def handlePieSplat(self):
		if self.splat:
			self.splat.cleanup()
			self.splat = None
				
		self.splat = Actor("phase_3.5/models/props/splat-mod.bam",
						{"chan": "phase_3.5/models/props/splat-chan.bam"})
		self.splat_sfx = audio3d.loadSfx(self.hitsounds[self.pie_type])
		audio3d.attachSoundToObject(self.splat_sfx, self.splat)
		self.splat_sfx.play()
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

	def delSplat(self, task):
		if self.splat:
			self.splat.cleanup()
			self.splat = None
		return task.done

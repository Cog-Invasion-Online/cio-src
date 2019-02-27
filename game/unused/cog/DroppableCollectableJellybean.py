"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DroppableCollectableJellybean.py
@author Brian Lach
@date March 22, 2015

"""

from panda3d.core import VBase4, Vec3
from direct.directnotify.DirectNotifyGlobal import directNotify
from DroppableCollectableJellybeans import DroppableCollectableJellybeans
from direct.interval.IntervalGlobal import LerpHprInterval
import random

class DroppableCollectableJellybean(DroppableCollectableJellybeans):
	notify = directNotify.newCategory("DroppableCollectableJellybean")

	def __init__(self):
		DroppableCollectableJellybeans.__init__(self)
		self.bean = None
		self.spinIval = None
		self.collectSfx = base.loadSfx("phase_3.5/audio/sfx/ci_s_money_smallBucks.ogg")

	def loadObject(self):
		self.removeObject()
		self.bean = loader.loadModel("phase_5.5/models/estate/jellyBean.bam")
		self.bean.setTwoSided(1)
		self.bean.setScale(1.5)
		self.bean.setZ(1.0)
		self.bean.reparentTo(self)
		# Give the bean a completely random color.
		self.bean.setColor(
			VBase4(
				random.uniform(0, 1),
				random.uniform(0, 1),
				random.uniform(0, 1),
				1.0
			)
		)
		self.spin()

	def removeObject(self):
		if self.bean:
			self.bean.removeNode()
			self.bean = None

	def load(self):
		self.collectSfx = base.loadSfx("phase_3.5/audio/sfx/ci_s_money_smallBucks.ogg")
		DroppableCollectableJellybeans.load(self)

	def unload(self):
		self.stopSpin()
		DroppableCollectableJellybeans.unload(self)

	def spin(self):
		self.stopSpin()
		self.spinIval = LerpHprInterval(
			self.bean,
			duration = 3.0,
			hpr = Vec3(360, 0, 0),
			startHpr = (0, 0, 0),
		)
		self.spinIval.loop()

	def stopSpin(self):
		if self.spinIval:
			self.spinIval.finish()
			self.spinIval = None

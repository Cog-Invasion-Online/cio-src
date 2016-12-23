# Filename: BRWater.py
# Created by:  blach (02Jul15)

from pandac.PandaModules import VBase4, WindowProperties

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import LerpColorScaleInterval, Sequence, Wait, Func
from direct.gui.DirectGui import DirectWaitBar, DirectFrame, OnscreenText

from random import choice

class BRWater:
	notify = directNotify.newCategory("BRWater")

	def __init__(self, playground):
		self.playground = playground
		self.fsm = ClassicFSM(
			'BRWater',
			[
				State('off', self.enterOff, self.exitOff),
				State('freezeUp', self.enterFreezeUp, self.exitFreezeUp),
				State('coolDown', self.enterCoolDown, self.exitCoolDown),
				State('frozen', self.enterFrozen, self.exitFrozen)
			],
			'off', 'off'
		)
		self.fsm.enterInitialState()

		#base.localAvatar.audio3d

		self.freezeUpSfx = base.loadSfx('phase_8/audio/sfx/freeze_up.ogg')
		self.frozenSfxArray = [
			base.loadSfx('phase_8/audio/sfx/frozen_1.ogg'),
			base.loadSfx('phase_8/audio/sfx/frozen_2.ogg'),
			base.loadSfx('phase_8/audio/sfx/frozen_3.ogg')
		]
		self.coolSfxArray = [
			base.loadSfx('phase_8/audio/sfx/cool_down_1.ogg'),
			base.loadSfx('phase_8/audio/sfx/cool_down_2.ogg')
		]

		self.freezeUpSfx.setVolume(12)
		for sfx in self.frozenSfxArray:
			sfx.setVolume(12)
		for sfx in self.coolSfxArray:
			sfx.setVolume(12)
		#for sfx in self.frozenSfxArray:
		#	self.attachSound(sfx)
		#for sfx in self.coolSfxArray:
		#	self.attachSound(sfx)
		#self.attachSound(self.freezeUpSfx)

	def attachSound(self, sound):
		base.localAvatar.audio3d.attachSoundToObject(sound, base.localAvatar)

	def enterOff(self):
		self.playground.startWaterWatch()

	def exitOff(self):
		self.playground.stopWaterWatch()

	def loadIceCube(self):
		self.iceCube = loader.loadModel('phase_8/models/props/icecube.bam')
		for node in self.iceCube.findAllMatches('**/billboard*'):
			node.removeNode()
		for node in self.iceCube.findAllMatches('**/drop_shadow*'):
			node.removeNode()
		for node in self.iceCube.findAllMatches('**/prop_mailboxcollisions*'):
			node.removeNode()
		self.iceCube.reparentTo(base.localAvatar)
		self.iceCube.setScale(1.2, 1.0, base.localAvatar.getHeight() / 1.7)
		self.iceCube.setTransparency(1)
		self.iceCube.setColorScale(0.76, 0.76, 1.0, 0.0)

	def unloadIceCube(self):
		self.iceCube.removeNode()
		del self.iceCube

	def enterFreezeUp(self):
		length = 1.0
		base.playSfx(self.freezeUpSfx)
		self.fucsIval = Sequence(
			LerpColorScaleInterval(
				base.localAvatar.getGeomNode(),
				duration = length,
				colorScale = VBase4(0.5, 0.5, 1.0, 1.0),
				startColorScale = base.localAvatar.getGeomNode().getColorScale(),
				blendType = 'easeOut'
			),
			Func(self.fsm.request, 'frozen')
		)
		self.fucsIval.start()
		self.playground.startWaterWatch(0)

	def exitFreezeUp(self):
		self.fucsIval.pause()
		del self.fucsIval
		self.playground.stopWaterWatch()

	def enterFrozen(self):
		self.loadIceCube()
		base.cr.playGame.getPlace().fsm.request('stop', [0])
		base.localAvatar.stop()
		base.playSfx(choice(self.frozenSfxArray))
		self.iccsIval = LerpColorScaleInterval(
			self.iceCube,
			duration = 0.5,
			colorScale = VBase4(0.76, 0.76, 1.0, 1.0),
			startColorScale = self.iceCube.getColorScale(),
			blendType = 'easeInOut'
		)
		self.iccsIval.start()
		props = WindowProperties()
		props.setCursorHidden(True)
		base.win.requestProperties(props)
		self.frame = DirectFrame(pos = (0, 0, 0.7))
		self.powerBar = DirectWaitBar(frameColor = (1, 1, 1, 1), range = 100, value = 0, scale = (0.4, 0.5, 0.25), parent = self.frame, barColor = (0.55, 0.7, 1.0, 1.0))
		self.label = OnscreenText(text = "SHAKE MOUSE", shadow = (0, 0, 0, 1), fg = (0.55, 0.7, 1.0, 1.0), pos = (0, -0.1, 0), parent = self.frame)
		taskMgr.add(self.__watchMouseMovement, 'BRWater-watchMouseMovement')
		taskMgr.add(self.__lowerPowerBar, 'BRWater-lowerPowerBar')
		mw = base.mouseWatcherNode
		if mw.hasMouse():
			self.lastMouseX = mw.getMouseX()

	def __lowerPowerBar(self, task):
		if self.powerBar['value'] <= 0:
			self.powerBar.update(0)
		decrement = 1
		self.powerBar.update(self.powerBar['value'] - decrement)
		task.delayTime = 0.1
		return task.again

	def __watchMouseMovement(self, task):
		if self.powerBar['value'] >= self.powerBar['range']:
			self.fsm.request('coolDown', [1])
			return task.done
		mw = base.mouseWatcherNode
		if mw.hasMouse():
			if not self.lastMouseX or self.lastMouseX != mw.getMouseX():
				value = 3 * self.lastMouseX - mw.getMouseX()
				self.lastMouseX = mw.getMouseX()
				self.powerBar.update(self.powerBar['value'] + abs(value))
		return task.cont

	def exitFrozen(self):
		props = WindowProperties()
		props.setCursorHidden(False)
		base.win.requestProperties(props)
		self.iccsIval.pause()
		del self.iccsIval
		self.unloadIceCube()
		taskMgr.remove('BRWater-lowerPowerBar')
		taskMgr.remove('BRWater-watchMouseMovement')
		self.label.destroy()
		del self.label
		self.powerBar.destroy()
		del self.powerBar
		self.frame.destroy()
		del self.frame
		del self.lastMouseX
		base.cr.playGame.getPlace().fsm.request('walk')
		base.localAvatar.b_setAnimState('neutral')

	def enterCoolDown(self, fromFrozen = 0):
		if fromFrozen:
			self.loadIceCube()
			self.iceCube.setColorScale(0.76, 0.76, 1.0, 1.0)
			self.iccdIval = LerpColorScaleInterval(
				self.iceCube,
				duration = 0.5,
				colorScale = VBase4(0.76, 0.76, 1.0, 0.0),
				startColorScale = self.iceCube.getColorScale(),
				blendType = 'easeInOut'
			)
			self.iccdIval.start()
		length = 1.0
		base.playSfx(choice(self.coolSfxArray))
		self.cdcsIval = Sequence(
			LerpColorScaleInterval(
				base.localAvatar.getGeomNode(),
				duration = length,
				colorScale = VBase4(1.0, 1.0, 1.0, 1.0),
				startColorScale = base.localAvatar.getGeomNode().getColorScale(),
				blendType = 'easeOut'
			),
			Func(self.fsm.request, 'off')
		)
		self.cdcsIval.start()

	def exitCoolDown(self):
		if hasattr(self, 'iccdIval'):
			self.iccdIval.pause()
			del self.iccdIval
			self.unloadIceCube()
		self.cdcsIval.pause()
		del self.cdcsIval

	def cleanup(self):
		self.fsm.requestFinalState()
		self.playground.stopWaterWatch()
		del self.fsm
		del self.freezeUpSfx
		del self.frozenSfxArray
		del self.coolSfxArray
		del self.playground

"""

  Filename: VicePresident.py
  Created by: blach (26Apr15)

"""

from panda3d.core import NodePath, Vec3
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.fsm.ClassicFSM import ClassicFSM
from direct.interval.IntervalGlobal import Sequence, Func, Wait, ActorInterval, LerpScaleInterval
from direct.showbase import Audio3DManager
from direct.distributed import DelayDelete

from lib.coginvasion.avatar.Avatar import Avatar
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval, NPCLookInterval

class VicePresident(Avatar):
	notify = directNotify.newCategory("VicePresident")

	def __init__(self):
		Avatar.__init__(self)
		self.fsm = ClassicFSM('VicePresident', [State('off', self.enterOff, self.exitOff),
			State('throwGear', self.enterThrowGear, self.exitThrowGear),
			State('neutral', self.enterNeutral, self.exitNeutral),
			State('jump', self.enterJump, self.exitJump),
			State('emerge', self.enterEmerge, self.exitEmerge),
			State('knockDown', self.enterKnockDown, self.exitKnockDown),
			State('riseUp', self.enterRiseUp, self.exitRiseUp)], 'off', 'off')
		self.fsm.enterInitialState()
		self.track = None
		self.treads = None
		self.rearDoor = None
		self.frontDoor = None
		self.gearModel = None
		self.gearThrowIval = None
		self.knockedDown = False
		self.chirps = base.audio3d.loadSfx("phase_4/audio/sfx/SZ_TC_bird1.mp3")
		base.audio3d.attachSoundToObject(self.chirps, self)
		self.vp_torso_node = NodePath('vp_torso_node')

	def enterOff(self):
		pass

	def exitOff(self):
		pass

	def enterRiseUp(self, ts = 0):
		if hasattr(self, 'uniqueName'):
			name = self.uniqueName('vpRiseUp')
		else:
			name = 'vpRiseUp'
		sfx = base.audio3d.loadSfx("phase_9/audio/sfx/CHQ_VP_raise_up.mp3")
		base.audio3d.attachSoundToObject(sfx, self)
		self.track = Sequence(
			Func(base.playSfx, sfx),
			ActorInterval(
				self,
				"up"
			),
			name = name
		)
		self.knockedDown = False
		self.track.setDoneEvent(self.track.getName())
		self.acceptOnce(self.track.getDoneEvent(), self.fsm.request, ["neutral"])
		self.track.start(ts)

	def exitRiseUp(self):
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None

	def enterKnockDown(self, ts = 0):
		if hasattr(self, 'uniqueName'):
			name = self.uniqueName('vpKnockDown')
		else:
			name = 'vpKnockDown'
		sfx = base.audio3d.loadSfx("phase_5/audio/sfx/AA_sound_aoogah.mp3")
		base.audio3d.attachSoundToObject(sfx, self)
		self.track = Sequence(
			Func(base.playSfx, sfx),
			ActorInterval(
				self,
				"fall"
			),
			name = name
		)
		self.knockedDown = True
		self.track.setDoneEvent(self.track.getName())
		self.acceptOnce(self.track.getDoneEvent(), self.fsm.request, ["neutral"])
		self.track.start(ts)

	def exitKnockDown(self):
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None

	def enterEmerge(self, ts = 0):
		if hasattr(self, 'uniqueName'):
			name = self.uniqueName('emergeTrack')
		else:
			name = 'emergeTrack'
		self.setScale(0.1)
		emergeSfx = base.audio3d.loadSfx("phase_5/audio/sfx/TL_train_track_appear.mp3")
		base.audio3d.attachSoundToObject(emergeSfx, self)
		self.track = Sequence(
			Func(base.playSfx, emergeSfx),
			LerpScaleInterval(
				self,
				duration = 1.2,
				scale = 1.0,
				startScale = 0.05,
				blendType = 'easeOut'
			),
			name = name
		)
		self.track.setDoneEvent(self.track.getName())
		self.acceptOnce(self.track.getDoneEvent(), self.fsm.request, ["neutral"])
		self.track.start(ts)
		self.loop('stand-angry')

	def exitEmerge(self):
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None

	def enterNeutral(self, ts = 0):
		if self.getCurrentAnim() != 'stand-angry':
			if self.knockedDown:
				base.playSfx(self.chirps, looping = 1)
				self.loop("dn_neutral")
			else:
				self.loop("stand-angry")
		self.track = NPCLookInterval(
			self.vp_torso_node,
			Vec3(0, 0, 0),
			blendType = 'easeInOut',
			name = 'lookAtCenter',
			isBackwards = False
		)
		self.track.start(ts)

	def exitNeutral(self):
		self.stop()
		self.chirps.stop()

	def enterJump(self, ts = 0):
		if hasattr(self, 'uniqueName'):
			name = self.uniqueName('vpJump')
		else:
			name = 'vpJump'
		jumpSfx = base.audio3d.loadSfx("phase_5/audio/sfx/General_throw_miss.mp3")
		landSfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.mp3")
		base.audio3d.attachSoundToObject(jumpSfx, self)
		base.audio3d.attachSoundToObject(landSfx, self)
		self.track = Sequence(
			Func(self.play, "jump"),
			Func(base.playSfx, jumpSfx),
			Wait(1.2),
			Func(base.playSfx, landSfx),
			Wait(1.8),
			name = name
		)
		self.track.setDoneEvent(self.track.getName())
		self.acceptOnce(self.track.getDoneEvent(), self.fsm.request, ["neutral"])
		self.track.start(ts)

	def exitJump(self):
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None

	def enterThrowGear(self, point, ts = 0):
		lookNode = render.attachNewNode('pointNode')
		lookNode.setPos(point)
		#self.gearModel.reparentTo(render)
		#self.gearModel.setPos(point)
		throwSfx = base.audio3d.loadSfx("phase_9/audio/sfx/CHQ_VP_frisbee_gears.mp3")
		base.audio3d.attachSoundToObject(throwSfx, self)
		if hasattr(self, 'uniqueName'):
			name = self.uniqueName('vpThrowGear')
		else:
			name = 'vpThrowGear'
		self.track = Sequence(
			NPCLookInterval(
				self.vp_torso_node,
				lookNode,
				blendType = 'easeInOut',
				isBackwards = False
			),
			Func(VicePresident.throwGear, self, point),
			Func(base.playSfx, throwSfx),
			ActorInterval(self, "throw"),
			name = name
		)
		self.track.setDoneEvent(self.track.getName())
		self.acceptOnce(self.track.getDoneEvent(), self.fsm.request, ["neutral"])
		self.track.start(ts)
		lookNode.removeNode()
		del lookNode

	def throwGear(self, point):
		self.gearModel.reparentTo(self.getPart("body"))
		self.gearModel.setX(0.0)
		self.gearModel.setY(-2)
		self.gearModel.setZ(5)
		self.gearModel.setPos(self.gearModel.getPos(render))
		self.gearModel.reparentTo(render)
		self.gearModel.show()
		self.gearModel.lookAt(point)
		if self.gearThrowIval:
			self.gearThrowIval.finish()
			self.gearThrowIval = None
		self.gearThrowIval = NPCWalkInterval(
			self.gearModel,
			point,
			durationFactor = 0.01,
			fluid = 1,
			lookAtTarget = False
		)
		self.gearThrowIval.start()

	def exitThrowGear(self):
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None

	def destroy(self):
		if 'head' in self._Actor__commonBundleHandles:
			del self._Actor__commonBundleHandles['head']
		if 'body' in self._Actor__commonBundleHandles:
			del self._Actor__commonBundleHandles['body']
		if 'legs' in self._Actor__commonBundleHandles:
			del self._Actor__commonBundleHandles['legs']
		if self.treads:
			self.treads.removeNode()
			self.treads = None
		if self.gearThrowIval:
			self.gearThrowIval.finish()
			self.gearThrowIval = None
		if self.gearModel:
			self.gearModel.removeNode()
			self.gearModel = None
		if self.track:
			self.ignore(self.track.getDoneEvent())
			self.track.finish()
			self.track = None
		self.rearDoor = None
		self.frontDoor = None
		if self.vp_torso_node:
			self.vp_torso_node.removeNode()
			self.vp_torso_node = None
		self.removePart("head")
		self.removePart("body")
		self.removePart("legs")

	def generate(self):
		self.generateLegs()
		self.generateBody()
		self.generateHead()
		self.generateTreads()
		self.generateGear()
		self.parentParts()

	def parentParts(self):
		self.attach('head', 'body', 'joint34')
		self.treads.reparentTo(self.getPart("legs").find('**/joint_axle'))
		self.vp_torso_node.reparentTo(self.getPart("legs").find('**/joint_legs'))
		self.getPart("body").reparentTo(self.vp_torso_node)
		self.getPart("body").setH(180)

		self.frontDoor.setR(-80)
		self.rearDoor.setR(77)

	def generateGear(self):
		self.gearModel = loader.loadModel("phase_9/models/char/gearProp.bam")
		self.gearModel.setScale(0.25)
		self.gearModel.hide()

	def generateTreads(self):
		self.treads = loader.loadModel("phase_9/models/char/bossCog-treads.bam")

	def generateLegs(self):
		self.loadModel("phase_9/models/char/bossCog-legs-zero.bam", "legs")
		self.loadAnims(
			{
				"stand-angry": "phase_9/models/char/bossCog-legs-Fb_neutral.bam",
				"stand-happy": "phase_9/models/char/bossCog-legs-Ff_neutral.bam",
				"jump":"phase_9/models/char/bossCog-legs-Fb_jump.bam",
				"throw": "phase_9/models/char/bossCog-legs-Fb_UpThrow.bam",
				"fall": "phase_9/models/char/bossCog-legs-Fb_firstHit.bam",
				"up": "phase_9/models/char/bossCog-legs-Fb_down2Up.bam",
				"dn_neutral": "phase_9/models/char/bossCog-legs-Fb_downNeutral.bam",
				"dn_throw": "phase_9/models/char/bossCog-legs-Fb_DownThrow.bam",
				"speech": "phase_9/models/char/bossCog-legs-Ff_speech.bam",
				"wave": "phase_9/models/char/bossCog-legs-wave.bam",
				"downhit": "phase_9/models/char/bossCog-legs-Fb_firstHit.bam"
			},
			"legs"
		)

		self.frontDoor = self.controlJoint(None, "legs", "joint_doorFront")
		self.rearDoor = self.controlJoint(None, "legs", "joint_doorRear")

	def generateBody(self):
		self.loadModel("phase_9/models/char/sellbotBoss-torso-zero.bam", "body")
		self.loadAnims(
			{
				"stand-angry": "phase_9/models/char/bossCog-torso-Fb_neutral.bam",
				"stand-happy": "phase_9/models/char/bossCog-torso-Ff_neutral.bam",
				"jump": "phase_9/models/char/bossCog-torso-Fb_jump.bam",
				"throw": "phase_9/models/char/bossCog-torso-Fb_UpThrow.bam",
				"fall": "phase_9/models/char/bossCog-torso-Fb_firstHit.bam",
				"up": "phase_9/models/char/bossCog-torso-Fb_down2Up.bam",
				"dn_neutral": "phase_9/models/char/bossCog-torso-Fb_downNeutral.bam",
				"dn_throw": "phase_9/models/char/bossCog-torso-Fb_DownThrow.bam",
				"speech": "phase_9/models/char/bossCog-torso-Ff_speech.bam",
				"wave": "phase_9/models/char/bossCog-torso-wave.bam",
				"downhit": "phase_9/models/char/bossCog-torso-Fb_firstHit.bam"
			},
			"body"
		)

	def generateHead(self):
		self.loadModel("phase_9/models/char/sellbotBoss-head-zero.bam", "head")
		self.loadAnims(
			{
				"stand-angry": "phase_9/models/char/bossCog-head-Fb_neutral.bam",
				"stand-happy": "phase_9/models/char/bossCog-head-Ff_neutral.bam",
				"jump": "phase_9/models/char/bossCog-head-Fb_jump.bam",
				"throw": "phase_9/models/char/bossCog-head-Fb_UpThrow.bam",
				"fall": "phase_9/models/char/bossCog-head-Fb_firstHit.bam",
				"up": "phase_9/models/char/bossCog-head-Fb_down2Up.bam",
				"dn_neutral": "phase_9/models/char/bossCog-head-Fb_downNeutral.bam",
				"dn_throw": "phase_9/models/char/bossCog-head-Fb_DownThrow.bam",
				"speech": "phase_9/models/char/bossCog-head-Ff_speech.bam",
				"wave": "phase_9/models/char/bossCog-head-wave.bam",
				"downhit": "phase_9/models/char/bossCog-head-Fb_firstHit.bam"
			},
			"head"
		)

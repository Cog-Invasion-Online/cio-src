########################################
# Filename: DistributedMickey.py
# Created by: blach (??Jun14)
########################################

from lib.coginvasion.globals import CIGlobals
from direct.actor.Actor import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.gui.DirectGui import *
import random
from lib.coginvasion.toon.ChatBalloon import ChatBalloon
from lib.coginvasion.toon.LabelScaler import LabelScaler
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.showbase.ShadowPlacer import ShadowPlacer

class DistributedMickey(DistributedSmoothNode):

	def __init__(self, cr):
		self.cr = cr
		DistributedSmoothNode.__init__(self, cr)
		NodePath.__init__(self, 'Mickey')
		self.name = "Mickey"
		self.anim = ""
		self.chat = ""

		self.mickey = Actor("phase_3/models/char/mickey-1200.bam",
						{"neutral": "phase_3/models/char/mickey-wait.bam",
						"walk": "phase_3/models/char/mickey-walk.bam",
						"run": "phase_3/models/char/mickey-run.bam",
						"left-start": "phase_3.5/models/char/mickey-left-start.bam",
						"left": "phase_3.5/models/char/mickey-left.bam",
						"right-start": "phase_3.5/models/char/mickey-right-start.bam",
						"right": "phase_3.5/models/char/mickey-right.bam"})
		self.mickeyEye = self.mickey.controlJoint(None, "modelRoot", "joint_pupilR")
		self.mickeyEye.setY(0.025)
		self.mickey.reparentTo(self)
		self.mickey.setScale(1.25)

		for bundle in self.mickey.getPartBundleDict().values():
			bundle = bundle['modelRoot'].getBundle()
			earNull = bundle.findChild('sphere3')
			if not earNull:
				earNull = bundle.findChild('*sphere3')
			earNull.clearNetTransforms()

		for bundle in self.mickey.getPartBundleDict().values():
			charNodepath = bundle['modelRoot'].partBundleNP
			bundle = bundle['modelRoot'].getBundle()
			earNull = bundle.findChild('sphere3')
			if not earNull:
				earNull = bundle.findChild('*sphere3')
			ears = charNodepath.find('**/sphere3')
			if ears.isEmpty():
				ears = charNodepath.find('**/*sphere3')
			ears.clearEffect(CharacterJointEffect.getClassType())
			earRoot = charNodepath.attachNewNode('earRoot')
			earPitch = earRoot.attachNewNode('earPitch')
			earPitch.setP(40.0)
			ears.reparentTo(earPitch)
			earNull.addNetTransform(earRoot.node())
			ears.clearMat()
			ears.node().setPreserveTransform(ModelNode.PTNone)
			ears.setP(-40.0)
			ears.flattenMedium()
			ears.setBillboardAxis()

		self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
		self.shadow.setScale(0.55)
		self.shadow.flattenMedium()
		self.shadow.setBillboardAxis(4)
		try:
			self.shadowPlacer = ShadowPlacer(base.cTrav, self.shadow, base.wall_mask, base.floor_mask)
			self.shadowPlacer.on()
		except:
			pass
		self.shadow.reparentTo(self)

		cs = CollisionSphere(0, 0, 0, 2)
		cnode = CollisionNode('mickeyCNode')
		cnode.addSolid(cs)
		rs = CollisionRay(0, 0, 2, 0, 0, -1)
		rnode = CollisionNode('mickeyRNode')
		rnode.addSolid(rs)
		self.cnp = self.attachNewNode(cnode)
		self.cnp.setZ(0.75)
		self.rnp = self.attachNewNode(rnode)

	def mickeyCollisions(self):
		self.cnp.setCollideMask(BitMask32(0))
		self.cnp.node().setFromCollideMask(CIGlobals.WallBitmask)
		self.rnp.setCollideMask(BitMask32(0))
		self.rnp.node().setFromCollideMask(CIGlobals.FloorBitmask)

		ss = CollisionSphere(0,0,0,10)
		snode = CollisionNode('mickeySNode')
		snode.addSolid(ss)
		self.snp = self.attachNewNode(snode)
		self.snp.setZ(0.75)
		self.snp.setCollideMask(BitMask32(0))
		self.snp.node().setFromCollideMask(CIGlobals.EventBitmask)

		pusher = CollisionHandlerPusher()
		pusher.setInPattern("%in")
		pusher.addCollider(self.cnp, self)
		floor = CollisionHandlerFloor()
		floor.setInPattern("%in")
		floor.addCollider(self.rnp, self)
		event = CollisionHandlerEvent()
		event.setInPattern("%fn-into")
		event.setOutPattern("%fn-out")
		base.cTrav.addCollider(self.cnp, pusher)
		base.cTrav.addCollider(self.rnp, floor)
		base.cTrav.addCollider(self.snp, event)

	def setName(self, name):
		self.name = name
		if name == "":
			return
		elif self.name == "minnie":
			self.name = "Minnie"
		try:
			self.nameTag.remove()
			del self.nameTag
		except:
			pass
		self.it = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf")
		self.nameTag = DirectLabel(text=self.name, text_fg=(0.992188, 0.480469, 0.167969, 1.0), text_bg=(0.75, 0.75, 0.75, 0.5), text_wordwrap=8, text_decal=True, relief=None, parent=self)
		self.nameTag.setPos(0, 0, 5)
		self.nameTag.setBillboardPointEye()
		LS = LabelScaler()
		LS.resize(self.nameTag)
	def b_setName(self, name):
		self.d_setName(name)
		self.setName(name)
	def d_setName(self, name):
		self.sendUpdate("setName", [name])

	def setChat(self, chat):
		if chat == "":
			return
		self.nameTag.hide()
		try:
			self.bubble.remove()
			taskMgr.remove("RemoveMickeyChat-" + str(self.random_taskid))
		except:
			pass
		self.chat = chat
		self.it = loader.loadFont(CIGlobals.ToonFont, lineHeight=CIGlobals.ToonFontLineHeight)
		b = loader.loadTexture("phase_3/maps/chatbubble.jpg", "phase_3/maps/chatbubble_a.rgb")

		self.balloon_sfx = loader.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.mp3")
		self.balloon_sfx.play()

		self.dial = loader.loadSfx("phase_3/audio/dial/mickey.wav")

		self.dial.play()

		self.box = loader.loadModel(CIGlobals.ChatBubble)
		self.ChatBalloon = ChatBalloon(self.box)
		LS = LabelScaler()
		self.bubble = self.ChatBalloon.generate(chat, self.it)
		LS.resize(self.bubble)
		self.bubble.reparentTo(self)
		self.bubble.setZ(self.nameTag.getZ() - 0.3)
		self.bubble.setBillboardPointEye()
		self.random_taskid = random.randint(0,10000000000000000000000000000000000000000000000000000000000000000000000)
		taskMgr.doMethodLater(7, self.delChat, "RemoveMickeyChat-" + str(self.random_taskid))
	def delChat(self, task):
		self.chat = ""
		self.nameTag.show()
		self.bubble.remove()
		return task.done
	def b_setChat(self, chat):
		self.d_setChat(chat)
		self.setChat(chat)
	def d_setChat(self, chat):
		self.sendUpdate("setChat", [chat])
	def getChat(self):
		return self.chat

	def setAnimState(self, anim):
		self.anim = anim
		if "start" in anim:
			self.mickey.play(anim)
		self.mickey.loop(anim)
	def b_setAnimState(self, anim):
		self.d_setAnimState(anim)
		self.setAnimState(anim)
	def d_setAnimState(self, anim):
		self.sendUpdate("setAnimState", [anim])
	def getAnimState(self):
		return self.anim

	def announceGenerate(self):
		DistributedSmoothNode.announceGenerate(self)

		self.reparentTo(render)
	def generate(self):
		DistributedSmoothNode.generate(self)

		self.activateSmoothing(True, False)
		self.startSmooth()
	def disable(self):
		self.stopSmooth()
		self.detachNode()
		DistributedSmoothNode.disable(self)
	def delete(self):
		self.mickey = None
		DistributedSmoothNode.delete(self)

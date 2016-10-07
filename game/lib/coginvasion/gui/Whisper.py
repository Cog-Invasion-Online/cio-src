"""

  Filename: Whisper.py
  Created by: blach (??Aug14)

"""

from pandac.PandaModules import Point3

from direct.interval.SoundInterval import SoundInterval

from lib.coginvasion.toon.ChatBalloonOld import ChatBalloon
from lib.coginvasion.globals import CIGlobals

import random
import math

class Whisper:
	LENGTH_FACTOR = 0.6

	def createSystemMessage(self, message, important = 1):
		try:
			taskMgr.remove("clearSystemMessage-" + self.taskName)
			self.bubble.remove_node()
			self.bubble = None
		except:
			pass
		self.taskName = str(random.uniform(0, 10101010100))
		msg_color = (0.8, 0.3, 0.6, 0.6)
		sysmsg_data = [[Point3(0.075, 0, -0.2), base.a2dLeftCenter],
			[Point3(-0.6, 0, -0.7), base.a2dRightCenter],
			[Point3(-0.6, 0, -0.2), base.a2dRightCenter],
			[Point3(0.075, 0, -0.7), base.a2dLeftCenter],
			[Point3(0.35, 0, 0.2), base.a2dBottomCenter],
			[Point3(-0.2, 0, 0.2), base.a2dBottomCenter],
			[Point3(-0.8, 0, 0.2), base.a2dBottomCenter]]
		data = random.choice(sysmsg_data)
		sfx = loader.loadSfx("phase_3.5/audio/sfx/GUI_whisper_3.ogg")
		SoundInterval(sfx).start()
		length = math.sqrt(len(message)) / self.LENGTH_FACTOR
		self.bubble = ChatBalloon(loader.loadModel("phase_3/models/props/chatbox_noarrow.bam")).generate(message, CIGlobals.getToonFont(), balloonColor=msg_color)
		self.bubble.reparent_to(data[1])
		self.bubble.set_pos(data[0])
		self.bubble.set_scale(0.05)

		taskMgr.doMethodLater(length, self.clearSystemMessage, "clearSystemMessage-" + self.taskName)

	def clearSystemMessage(self, task):
		self.bubble.remove_node()
		self.bubble = None
		return task.done

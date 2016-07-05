
###############################################################
#															  #
#                    ABANDONED PROJECT:                       #
#                     "VP Controller"                         #
#															  #
#                  Started in March, 2014                     #
#															  #
#                                                             #
#                        FEATURES:                            #
#                 Control the Toontown VP.                    #
#                                                             #
#                                                             #
#                          BUGS:                              #
#              Audio cuts off on some actions.                #
#                                                             #
###############################################################

from pandac.PandaModules import *
loadPrcFile('config/config_client.prc')

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.actor.Actor import *
from direct.task import *
from math import *
from direct.showbase.ShowBase import *
from direct.task import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from pandac.PandaModules import LMatrix4f
from panda3d.core import LMatrix4f
from direct.gui.OnscreenText import *
from direct.actor.Actor import *
from direct.showbase.DirectObject import *
from direct.gui.DirectGui import *
from direct.interval.MetaInterval import Sequence

gear_1 = loader.loadModel("phase_9/models/char/gearProp.bam")

vp_down = loader.loadSfx("phase_5/audio/sfx/AA_sound_aoogah.mp3")
vp_up = loader.loadSfx("phase_9/audio/sfx/CHQ_VP_raise_up.mp3")

impress_bt = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf")
click = loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.mp3")
rollover = loader.loadSfx("phase_3/audio/sfx/GUI_rollover.mp3")

gear_throw = loader.loadSfx("phase_9/audio/sfx/CHQ_VP_frisbee_gears.mp3")
gear_shower = loader.loadSfx("phase_9/audio/sfx/CHQ_VP_raining_gears.mp3")

jump_start = loader.loadSfx("phase_5/audio/sfx/General_throw_miss.mp3")
jump_end = loader.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.mp3")
class cat:
	def __init__(self):
		self.button_img = loader.loadModel("phase_3/models/gui/quit_button.bam")
		self.music = loader.loadSfx("phase_7/audio/bgm/encntr_suit_winning_indoor.ogg")
		self.music.setVolume(1)
		self.music.setLoop(True)
		self.music.play()
		base.disableMouse()
		camera.setPos(-0.3, -45.6, 15.9)
		camera.setHpr(0, 0, 0)
		#self.get_pos_button = DirectButton(text="GetPos", command=self.give_pos, scale=0.08, pos=(1, 0, 0))
		#self.get_hpr_button = DirectButton(text="GetHpr", command=self.give_hpr, scale=0.08, pos=(-1, 0, 0))
		
		self.vp_torso = Actor("phase_9/models/char/sellbotBoss-torso-zero.bam",
							{"torso-stand-angry": "phase_9/models/char/bossCog-torso-Fb_neutral.bam",
							"torso-stand-happy": "phase_9/models/char/bossCog-torso-Ff_neutral.bam",
							"torso-jump": "phase_9/models/char/bossCog-torso-Fb_jump.bam",
							"torso-throw": "phase_9/models/char/bossCog-torso-Fb_UpThrow.bam",
							"torso-fall": "phase_9/models/char/bossCog-torso-Fb_firstHit.bam",
							"torso-up": "phase_9/models/char/bossCog-torso-Fb_down2Up.bam",
							"torso-dn_neutral": "phase_9/models/char/bossCog-torso-Fb_downNeutral.bam",
							"torso-dn_throw": "phase_9/models/char/bossCog-torso-Fb_DownThrow.bam",
							"torso-speech": "phase_9/models/char/bossCog-torso-Ff_speech.bam",
							"torso-wave": "phase_9/models/char/bossCog-torso-wave.bam",
							"torso-downhit": "phase_9/models/char/bossCog-torso-Fb_firstHit.bam"})
		
		self.vp_head_joint = self.vp_torso.find('**/joint34')
		self.vp_hand_joint = self.vp_torso.find('**/joint_pelvis')
		gear_1.reparentTo(self.vp_torso)
		gear_1.setScale(0.5)
		gear_1.setY(-2)
		gear_1.setZ(5)
		gear_1.hide()
		
		self.vp_head = Actor("phase_9/models/char/sellbotBoss-head-zero.bam",
							{"head-stand-angry": "phase_9/models/char/bossCog-head-Fb_neutral.bam",
							"head-stand-happy": "phase_9/models/char/bossCog-head-Ff_neutral.bam",
							"head-jump": "phase_9/models/char/bossCog-head-Fb_jump.bam",
							"head-throw": "phase_9/models/char/bossCog-head-Fb_UpThrow.bam",
							"head-fall": "phase_9/models/char/bossCog-head-Fb_firstHit.bam",
							"head-up": "phase_9/models/char/bossCog-head-Fb_down2Up.bam",
							"head-dn_neutral": "phase_9/models/char/bossCog-head-Fb_downNeutral.bam",
							"head-dn_throw": "phase_9/models/char/bossCog-head-Fb_DownThrow.bam",
							"head-speech": "phase_9/models/char/bossCog-head-Ff_speech.bam",
							"head-wave": "phase_9/models/char/bossCog-head-wave.bam",
							"head-downhit": "phase_9/models/char/bossCog-head-Fb_firstHit.bam"})
		self.vp_head.reparentTo(self.vp_head_joint)
		
		self.vp_legs = Actor("phase_9/models/char/bossCog-legs-zero.bam",
							{"legs-stand-angry": "phase_9/models/char/bossCog-legs-Fb_neutral.bam",
							"legs-stand-happy": "phase_9/models/char/bossCog-legs-Ff_neutral.bam",
							"legs-jump":"phase_9/models/char/bossCog-legs-Fb_jump.bam",
							"legs-throw": "phase_9/models/char/bossCog-legs-Fb_UpThrow.bam",
							"legs-fall": "phase_9/models/char/bossCog-legs-Fb_firstHit.bam",
							"legs-up": "phase_9/models/char/bossCog-legs-Fb_down2Up.bam",
							"legs-dn_neutral": "phase_9/models/char/bossCog-legs-Fb_downNeutral.bam",
							"legs-dn_throw": "phase_9/models/char/bossCog-legs-Fb_DownThrow.bam",
							"legs-speech": "phase_9/models/char/bossCog-legs-Ff_speech.bam",
							"legs-wave": "phase_9/models/char/bossCog-legs-wave.bam",
							"legs-downhit": "phase_9/models/char/bossCog-legs-Fb_firstHit.bam"})
		self.vp_legs.reparentTo(render)
		
		self.vp_legs_joint = self.vp_legs.find('**/joint_legs')
		
		self.vp_torso.reparentTo(self.vp_legs_joint)
		self.emote = 'angry'
		self.vp_head.loop("head-stand-angry")
		self.vp_legs.loop("legs-stand-angry")
		self.vp_torso.loop("torso-stand-angry")
		
		self.btn_happy = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Happy", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(1, 0.8, 0.8), command=self.goto_happy)
		self.btn_angry = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Angry", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(1, 0.7, 0.7), command=self.goto_angry)
		self.btn_jump = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Jump", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(-1, 0.8, 0.8), command=self.goto_jump)
		self.btn_throw = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Throw", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(-1, 0.7, 0.7), command=self.vp_throw)
		self.btn_collapse = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Down", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(-1, 0.6, 0.6), command=self.vp_collapse)
		self.btn_up = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Up", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(-1, 0.5, 0.5), command=self.goto_up)
		self.btn_speech = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Speech", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(-1, 0.4, 0.4), command=self.goto_speech)
		
		self.btn_wave = DirectButton(geom=(self.button_img.find('**/QuitBtn_UP'),
											self.button_img.find('**/QuitBtn_DN'),
											self.button_img.find('**/QuitBtn_RLVR')), relief=None, clickSound=click, rolloverSound=rollover, scale=1, text="Wave", text_font=impress_bt, text_scale=0.059999999999999998, text_pos=(0, -0.015), pos=(-1, 0.3, 0.3), command=self.goto_wave)
		self.slider_turn = DirectSlider(range=(-150, 150), value=0, pageSize=20, command=self.turn_vp, scale=0.7, orientation=DGG.VERTICAL, pos=(1, -0.2, -0.2))
		self.find = self.vp_torso.findAllMatches('**')
		print self.find
		
	def goto_happy(self):
		taskMgr.add(self.vp_happy, "VP HAPPY")
		
	def goto_angry(self):
		taskMgr.add(self.vp_angry, "VP ANGRY")
		
	def goto_jump(self):
		taskMgr.add(self.vp_jump, "VP JUMP1")
		
	def goto_speech(self):
		taskMgr.add(self.vp_speech, "VP SPEECH")
		
	def goto_wave(self):
		taskMgr.add(self.vp_wave, "VP WAVE")
	def goto_up(self):
		taskMgr.add(self.vp_up, "VP WAVE")
		
	def turn_vp(self):
		self.vp_torso.setH(self.slider_turn['value'])
	
		
	def vp_happy(self, task):
		self.btn_happy.show()
		self.btn_angry.show()
		self.btn_jump.show()
		self.btn_throw.show()
		self.btn_collapse.show()
		self.btn_up.show()
		self.btn_speech.show()
		self.btn_wave.show()
		try:
			self.btn_stop_speech.remove()
		except:
			print("button does not exist")
		try:
			self.btn_stop_wave.remove()
		except:
			print("button does not exist")
		self.emote = 'happy'
		print self.emote
		self.vp_head.loop("head-stand-happy")
		self.vp_legs.loop("legs-stand-happy")
		self.vp_torso.loop("torso-stand-happy")
		try:
			if self.position == 'down':
				self.vp_head.loop("head-dn_neutral")
				self.vp_torso.loop("torso-dn_neutral")
				self.vp_legs.loop("legs-dn_neutral")
		except:
			print("var not set")
		return task.done
		
	def vp_angry(self, task):
		self.btn_happy.show()
		self.btn_wave.show()
		self.btn_angry.show()
		self.btn_jump.show()
		self.btn_throw.show()
		self.btn_collapse.show()
		self.btn_up.show()
		self.btn_speech.show()
		try:
			self.btn_stop_speech.remove()
		except:
			print("button does not exist")
		try:
			self.btn_stop_wave.remove()
		except:
			print("button does not exist")
		self.emote = 'angry'
		print self.emote
		self.vp_head.loop("head-stand-angry")
		self.vp_legs.loop("legs-stand-angry")
		self.vp_torso.loop("torso-stand-angry")
		try:
			if self.position == 'down':
				self.vp_head.loop("head-dn_neutral")
				self.vp_torso.loop("torso-dn_neutral")
				self.vp_legs.loop("legs-dn_neutral")
		except:
			print("var not set")
		return task.done
		
	def gear_hide(self, task):
		gear_1.hide()
		return task.done
		
	def vp_jump(self, task):
		try:
			if self.position == 'down':
				self.direction = 'jump'
				self.goto_up()
				return
		except:
			print("var not set")
		self.btn_happy.hide()
		self.btn_angry.hide()
		self.btn_wave.hide()
		self.btn_jump.hide()
		self.btn_throw.hide()
		self.btn_collapse.hide()
		self.btn_up.hide()
		self.btn_speech.hide()
		self.action = 'jump'
		print self.action
		self.position = 'up'
		self.vp_head.play("head-jump")
		self.vp_legs.play("legs-jump")
		self.vp_torso.play("torso-jump")
		jump_start.play()
		taskMgr.doMethodLater(1.2, self.vp_jump_end, "end sound")
		if self.emote == 'happy':
			taskMgr.doMethodLater(3, self.vp_happy, "Happy VP")
		if self.emote == 'angry':
			taskMgr.doMethodLater(3, self.vp_angry, "Angry VP")
		return task.done
		
	def vp_speech(self, task):
		self.btn_speech.hide()
		try:
			if self.position == 'down':
				self.direction = 'speech'
				self.goto_up()
				return
		except:
			print("var not set")
		self.btn_happy.hide()
		self.btn_angry.hide()
		self.btn_jump.hide()
		self.btn_throw.hide()
		self.btn_collapse.hide()
		self.btn_up.hide()
		self.btn_wave.hide()
		self.action = 'speech'
		print self.action
		self.vp_head.loop("head-speech")
		self.vp_legs.loop("legs-speech")
		self.vp_torso.loop("torso-speech")
		self.OK_ButtonImage = loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam")
		self.btn_stop_speech = DirectButton(geom=(self.OK_ButtonImage.find('**/CloseBtn_UP'),
													self.OK_ButtonImage.find('**/CloseBtn_DN'),
													self.OK_ButtonImage.find('**/CloseBtn_Rllvr')), rolloverSound=rollover, clickSound=click, relief=None, scale=1.5, pos=(-1, 0.4, 0.4), text="Stop", text_scale=0.05, text_font=impress_bt, text_pos=(0, -0.1, -0.1), command=self.stop_speech)
		return task.done
		
	def vp_wave(self, task):
		self.btn_speech.hide()
		self.btn_wave.hide()
		try:
			if self.position == 'down':
				self.direction = 'wave'
				self.goto_up()
				return
		except:
			print("var not set")
		self.btn_happy.hide()
		self.btn_angry.hide()
		self.btn_jump.hide()
		self.btn_throw.hide()
		self.btn_collapse.hide()
		self.btn_up.hide()
		self.action = 'wave'
		print self.action
		self.vp_head.loop("head-wave")
		self.vp_legs.loop("legs-wave")
		self.vp_torso.loop("torso-wave")
		self.OK_ButtonImage = loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam")
		self.btn_stop_wave = DirectButton(geom=(self.OK_ButtonImage.find('**/CloseBtn_UP'),
													self.OK_ButtonImage.find('**/CloseBtn_DN'),
													self.OK_ButtonImage.find('**/CloseBtn_Rllvr')), rolloverSound=rollover, clickSound=click, relief=None, scale=1.5, pos=(-1, 0.3, 0.3), text="Stop", text_scale=0.05, text_font=impress_bt, text_pos=(0, -0.1, -0.1), command=self.stop_wave)
		return task.done
		
	def stop_speech(self):
		if self.emote == 'happy':
			taskMgr.add(self.vp_happy, "VP HAPPY1")
		if self.emote == 'angry':
			taskMgr.add(self.vp_angry, "VP ANGRY1")
	def stop_wave(self):
		if self.emote == 'happy':
			taskMgr.add(self.vp_happy, "VP HAPPY2")
		if self.emote == 'angry':
			taskMgr.add(self.vp_angry, "VP ANGRY2")
	def vp_collapse(self):
		self.btn_happy.hide()
		self.btn_angry.hide()
		self.btn_jump.hide()
		self.btn_throw.hide()
		self.btn_collapse.hide()
		self.btn_up.hide()
		self.btn_speech.hide()
		self.btn_wave.hide()
		self.position = 'down'
		print self.position
		self.vp_head.play("head-fall")
		self.vp_torso.play("torso-fall")
		self.vp_legs.play("legs-fall")
		vp_down.play()
		if self.emote == 'happy':
			taskMgr.doMethodLater(3, self.vp_happy, "Happy VP")
		if self.emote == 'angry':
			taskMgr.doMethodLater(3, self.vp_angry, "Angry VP")
	def vp_up(self, task):
		try:
			if self.direction == 'jump':
				self.direction = None
				self.vp_head.play("head-up")
				self.vp_torso.play("torso-up")
				self.vp_legs.play("legs-up")
				taskMgr.doMethodLater(2.6, self.vp_jump, "VP JUMP")
		except:
			print("var not set")
		try:
			if self.direction == 'speech':
				self.direction = None
				self.vp_head.play("head-up")
				self.vp_torso.play("torso-up")
				self.vp_legs.play("legs-up")
				taskMgr.doMethodLater(2.6, self.vp_speech, "VP SPEECH")
		except:
			print("var not set")
		try:
			if self.direction == 'wave':
				self.direction = None
				self.vp_head.play("head-up")
				self.vp_torso.play("torso-up")
				self.vp_legs.play("legs-up")
				taskMgr.doMethodLater(2.6, self.vp_wave, "VP WAVE")
		except:
			print("var not set")
		self.btn_happy.hide()
		self.btn_angry.hide()
		self.btn_jump.hide()
		self.btn_wave.hide()
		self.btn_throw.hide()
		self.btn_collapse.hide()
		self.btn_up.hide()
		self.btn_speech.hide()
		self.position = 'up'
		print self.position
		self.vp_head.play("head-up")
		self.vp_torso.play("torso-up")
		self.vp_legs.play("legs-up")
		vp_up.play()
		if self.emote == 'happy':
			taskMgr.doMethodLater(2.6, self.vp_happy, "Happy VP")
		if self.emote == 'angry':
			taskMgr.doMethodLater(2.6, self.vp_angry, "Angry VP")
		return task.done
	def vp_throw(self):
		self.btn_speech.hide()
		self.btn_happy.hide()
		self.btn_collapse.hide()
		self.btn_angry.hide()
		self.btn_jump.hide()
		self.btn_wave.hide()
		self.btn_throw.hide()
		self.btn_up.hide()
		gear_1.show()
		gear_1_interval = gear_1.posInterval(2,
										Point3(0, -200, 5),
										startPos=Point3(0, -2, 5))
		gear_1_move = Sequence(gear_1_interval,
								name="gear_1_throw")
		gear_1_move.start()
		taskMgr.doMethodLater(2, self.gear_hide, "Hide Gear")
		self.action = 'throw'
		print self.action
		gear_throw.play()
		self.vp_head.play("head-throw")
		self.vp_legs.play("legs-throw")
		self.vp_torso.play("torso-throw")
		try:
			if self.position == 'down':
				self.vp_head.play("head-dn_throw")
				self.vp_torso.play("torso-dn_throw")
				self.vp_legs.play("legs-dn_throw")
		except:
			print("var not set")
		if self.emote == 'happy':
			taskMgr.doMethodLater(0.9, self.vp_happy, "Happy VP")
		if self.emote == 'angry':
			taskMgr.doMethodLater(0.9, self.vp_angry, "Angry VP")
			
	def vp_jump_end(self, task):
		jump_end.play()
		
	def give_pos(self):
		print camera.getPos()
		
	def give_hpr(self):
		print camera.getHpr()
		
c = cat()
base.run()

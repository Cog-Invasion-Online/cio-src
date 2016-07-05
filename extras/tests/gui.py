from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 16')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.gui.DirectGui import *
from lib.coginvasion.gui.Dialog import GlobalDialog
from direct.distributed.ClientRepository import ClientRepository
from direct.interval.IntervalGlobal import *
from lib.coginvasion.toon import ParticleLoader
from direct.showbase.Audio3DManager import Audio3DManager
from direct.actor.Actor import Actor
from lib.coginvasion.globals import CIGlobals
import sys

from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.npc.NPCGlobals import NPC_DNA

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

class game:
	process = 'client'
import __builtin__
__builtin__.game = game()

from direct.gui.DirectGui import *

base.cr = ClientRepository([])
base.cTrav = CollisionTraverser()
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)


base.cr.isShowingPlayerIds = False

base.enableParticles()
"""
box = DirectFrame()
gui = loader.loadModel('phase_3/models/gui/dialog_box_gui.bam')
box['image'] = gui
box['image_color'] = (1, 1, 0.75, 1)
box['image_scale'] = (2, 1, 1.3)

label = OnscreenText(text = 'Choose a Class', parent = box, pos = (0, 0.47, 0), font = CIGlobals.getToonFont(), scale = 0.1)
class_text = OnscreenText(text = '', parent = box, pos = (0, -0.1, 0), font = CIGlobals.getToonFont(), scale = 0.09)

def set_class_text(text, foo):
	class_text.setText(text)

toons_frame = DirectFrame(parent = box, scale = 0.65, pos = (-0.3, 0, 0.2))
toonup = DirectButton(relief = None, pressEffect = 0, parent = toons_frame,
	image = ('ci_class_selection/toonup_neutral.png',
			'ci_class_selection/toonup_hover.png',
			'ci_class_selection/toonup_hover.png',
			'ci_class_selection/toonup_neutral.png'),
	image_scale = (0.75, 1, 1),
	scale = 0.3, pos = (-0.74, 0, 0))
toonup.bind(DGG.ENTER, set_class_text, extraArgs = ['Toon-Up'])
toonup.bind(DGG.EXIT, set_class_text, extraArgs = [''])
trap = DirectButton(relief = None, pressEffect = 0, parent = toons_frame,
	image = ('ci_class_selection/trap_neutral.png',
			'ci_class_selection/trap_hover.png',
			'ci_class_selection/trap_hover.png',
			'ci_class_selection/trap_neutral.png'),
	image_scale = (0.9, 1, 1),
	scale = 0.27, pos = (-0.3, 0, -0.025))
trap.bind(DGG.ENTER, set_class_text, extraArgs = ['Trap'])
trap.bind(DGG.EXIT, set_class_text, extraArgs = [''])
sound = DirectButton(relief = None, pressEffect = 0, parent = toons_frame,
	image = ('ci_class_selection/sound_neutral.png',
			'ci_class_selection/sound_hover.png',
			'ci_class_selection/sound_hover.png',
			'ci_class_selection/sound_neutral.png'),
	image_scale = (1, 1, 1),
	scale = 0.27, pos = (0.2, 0, -0.025))
sound.bind(DGG.ENTER, set_class_text, extraArgs = ['Sound'])
sound.bind(DGG.EXIT, set_class_text, extraArgs = [''])
throw = DirectButton(relief = None, pressEffect = 0, parent = toons_frame,
	image = ('ci_class_selection/throw_neutral.png',
			'ci_class_selection/throw_hover.png',
			'ci_class_selection/throw_hover.png',
			'ci_class_selection/throw_neutral.png'),
	image_scale = (0.9, 1, 1),
	scale = 0.27, pos = (0.69, 0, -0.025))
throw.bind(DGG.ENTER, set_class_text, extraArgs = ['Throw'])
throw.bind(DGG.EXIT, set_class_text, extraArgs = [''])
squirt = DirectButton(relief = None, pressEffect = 0, parent = toons_frame,
	image = ('ci_class_selection/squirt_neutral.png',
			'ci_class_selection/squirt_hover.png',
			'ci_class_selection/squirt_hover.png',
			'ci_class_selection/squirt_neutral.png'),
	image_scale = (1, 1, 1),
	scale = 0.27, pos = (1.2, 0, -0.03))
squirt.bind(DGG.ENTER, set_class_text, extraArgs = ['Squirt'])
squirt.bind(DGG.EXIT, set_class_text, extraArgs = [''])
drop = DirectButton(relief = None, pressEffect = 0, parent = toons_frame,
	image = ('ci_class_selection/drop_neutral.png',
			'ci_class_selection/drop_hover.png',
			'ci_class_selection/drop_hover.png',
			'ci_class_selection/drop_neutral.png'),
	image_scale = (0.75, 1, 1),
	scale = 0.27, pos = (1.7, 0, -0.025))
drop.bind(DGG.ENTER, set_class_text, extraArgs = ['Drop'])
drop.bind(DGG.EXIT, set_class_text, extraArgs = [''])
"""
"""
base.setBackgroundColor(255.0 / 255, 255.0 / 255, 191.0 / 255)

flippy = Toon(base.cr)
flippy.setDNAStrand(NPC_DNA['Flippy'])
flippy.generateToon()
flippy.deleteShadow()
flippy.deleteShadow()
flippy.reparentTo(render)
flippy.pose('push-button', 53)
button = loader.loadModel('phase_3.5/models/props/button.bam')
button.reparentTo(flippy.find('**/def_joint_left_hold'))


megaphone = loader.loadModel('phase_5/models/props/megaphone.bam')

pivot = render.attachNewNode('megaphonepivot')
pivot.setPos(1, 0, -1)
megaphone.reparentTo(pivot)
megaphone.setPos(0, -5, 0)

track = Sequence(
	Parallel(
		LerpHprInterval(
			pivot,
			duration = 0.4,
			hpr = (180, 10, 90),
			startHpr = (140, -75, 90),
			blendType = 'easeOut'
		),
		LerpHprInterval(
			megaphone,
			duration = 0.4,
			hpr = (0, 0, 0),
			startHpr = (-50, 0, 0)
		)
	),
	Parallel(
		LerpHprInterval(
			pivot,
			duration = 1,
			hpr = (180, 11, 92),
			startHpr = (180, 10, 90),
			blendType = 'easeOut'
		),
		LerpPosInterval(
			pivot,
			duration = 1,
			pos = (1, 0.1, -1),
			startPos = (1, 0, -1),
			blendType = 'easeInOut'
		)
	),
	Parallel(
		LerpHprInterval(
			pivot,
			duration = 0.5,
			hpr = (140, 75, 90),
			startHpr = (180, 11, 92),
			blendType = 'easeOut'
		),
		LerpPosInterval(
			pivot,
			duration = 1,
			pos = (1, 0, -1),
			startPos = (1, 0.1, -1),
			blendType = 'easeInOut'
		)
	)
)
track.loop()

render.setAntialias(AntialiasAttrib.MMultisample)

def trans():
	flippy.setColorScale(0.5, 0.5, 0.5, 1.0)
def untrans():
	flippy.setColorScale(1.0, 1.0, 1.0, 1.0)
	
base.accept('u', untrans)
base.accept('t', trans)



text = OnscreenText(text = 'A guard has noticed you!', font = CIGlobals.getMickeyFont(), fg = (1, 0.9, 0.3, 1), pos = (0, 0.8, 0))
text.setScale(0.0)
def change_text_scale(num):
	text.setScale(num)
pulse = Sequence(
	LerpFunc(
		change_text_scale,
		duration = 0.3,
		toData = 0.12,
		fromData = 0.01,
		blendType = 'easeOut'
	),
	LerpFunc(
		change_text_scale,
		duration = 0.2,
		toData = 0.1,
		fromData = 0.12,
		blendType = 'easeInOut'
	)
)
sfx = base.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.mp3')
music = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
def spot():
	pulse.start()
	base.playSfx(sfx)
	base.playMusic(music)

base.accept('s', spot)
"""

font = CIGlobals.getMickeyFont()
box = loader.loadModel('phase_3/models/gui/dialog_box_gui.bam')
imp = CIGlobals.getToonFont()
geom = CIGlobals.getDefaultBtnGeom()
container = DirectFrame()
bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4),
	parent = container)
title = OnscreenText(
	text = "Vote  on  Game  Mode", pos = (0, 0.5, 0), font = font,
	scale = (0.12), parent = container, fg = (1, 0.9, 0.3, 1))
btnFrame = DirectFrame(parent = container, pos = (0.14, 0, 0))
casualFrame = DirectFrame(parent = btnFrame, pos = (-0.5, 0, 0))
ctfFrame = DirectFrame(parent = btnFrame, pos = (0.22, 0, 0))
casual = DirectButton(
	parent = casualFrame, relief = None, pressEffect = 0, 
	image = ('/c/Users/Brian/Pictures/ci_tb_teams/blue_neutral.png', 
			'/c/Users/Brian/Pictures/ci_tb_teams/blue_hover.png',
			'/c/Users/Brian/Pictures/ci_tb_teams/blue_hover.png'),
	image_scale = (0.9, 1, 1), scale = 0.4)
casual_votesLbl = OnscreenText(
	parent = casualFrame, text = "0", pos = (0, -0.46, 0), font = imp)
ctf = DirectButton(
	parent = ctfFrame, relief = None, pressEffect = 0, 
	image = ('/c/Users/Brian/Pictures/ci_tb_teams/red_neutral.png', 
			'/c/Users/Brian/Pictures/ci_tb_teams/red_hover.png',
			'/c/Users/Brian/Pictures/ci_tb_teams/red_hover.png'),
	image_scale = (0.9, 1, 1), scale = 0.4)
ctf_votesLbl = OnscreenText(
	parent = ctfFrame, text = "2", pos = (0, -0.46, 0), font = imp)

for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(16)
			except:
				pass
	except:
		continue

#base.oobe()
base.run()

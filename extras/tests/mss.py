from panda3d.core import *
loadPrcFileData('', 'audio-library-name p3miles_audio')
loadPrcFileData('', 'load-display pandagl')
from direct.showbase.ShowBase import ShowBase
base = ShowBase()
from direct.interval.IntervalGlobal import *

array = ['/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Factory_v1.ogg','/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Factory_v2.ogg','/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Factory_v3.ogg', '/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Entry_v1.ogg','/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Entry_v2.ogg','/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Entry_v3.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Entry_v2.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Entry_v3.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_9/audio/bgm/encntr_suit_HQ_nbrhood.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_11/audio/bgm/LB_courtyard.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_11/audio/bgm/LB_juryBG.ogg',
    '/c/Users/Brian/Documents/panda3d/build_test/phase_3.5/audio/bgm/TC_SZ.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_7/audio/bgm/tt_elevator.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_7/audio/bgm/encntr_general_bg_indoor.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_7/audio/bgm/encntr_toon_winning_indoor.ogg']
currentSong = -1
#music = loader.loadMusic(array[currentSong])
#music.setLoop(False)
#music.play()

music = None

def stopCurrentMusic():
	music.stop()
	
def playNextSong():
	global music
	global currentSong
	if music:
		music.stop()
	currentSong += 1
	music = loader.loadMusic(array[currentSong])
	music.setLoop(True)
	music.play()

base.accept("s", stopCurrentMusic)
base.accept("p", playNextSong)

#base.accept("PandaPaused", base.enableMusic, [False])
#base.accept("PandaRestarted", base.enableMusic, [True])

base.run()

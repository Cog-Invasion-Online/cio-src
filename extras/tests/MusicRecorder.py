"""

  Filename: MusicRecorder.py
  Created by: blach (26Apr15)

"""

from sendkeys import SendKeys

from panda3d.core import loadPrcFile, loadPrcFileData
loadPrcFile('/c/Users/Brian/Documents/panda3d/Panda3D-CI/etc/Config.prc')
loadPrcFileData('', 'audio-library-name p3miles_audio')
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.showbase.ShowBase import ShowBase
base = ShowBase()

START_KEY = '{F12}'
STOP_KEY = '{F12}'

print 'Recording start key: ' + START_KEY
print 'Recording stop key: ' + STOP_KEY

EXTENSION = '.mid'
print 'Music extension: ' + EXTENSION

BASE = ''
PHASES = [
    BASE + 'phase_3/audio/bgm/',
    BASE + 'phase_3.5/audio/bgm/',
    BASE + 'phase_4/audio/bgm/',
    BASE + 'phase_6/audio/bgm/',
    BASE + 'phase_7/audio/bgm/',
    BASE + 'phase_8/audio/bgm/',
    BASE + 'phase_9/audio/bgm/',
    BASE + 'phase_11/audio/bgm/',
    BASE + 'phase_12/audio/bgm/',
    BASE + 'phase_13/audio/bgm/'
]

print 'Base path: ' + BASE
print 'Phases: ' + str(PHASES)

import glob
import sys
import os
FILE_LIST = []

print 'Generating list of all music...'
for phase in PHASES:
    print 'Looking in: ' + phase
    print phase + '*' + EXTENSION
    array = glob.glob(phase + '*' + EXTENSION)
    for song in array:
        FILE_LIST.append(song)
    print 'I found: ' + str(array)
print 'Finished generating list.'

print 'Starting.'

#FILE_LIST.remove(FILE_LIST[0])
music = None
#music.play()
current_song = -1

def watch_song(task):
    if music.status() == music.READY:
        print 'Finished recording song: ' + FILE_LIST[current_song]
        # Wait a bit to end the recording because it will stop short.
        Sequence(Wait(0.75), Func(SendKeys.SendKeys, STOP_KEY)).start()
        if current_song == len(FILE_LIST) - 1:
            print 'Finished recording %d songs.' % len(FILE_LIST)
            base.shutdown()
            sys.exit()
            return task.done
        else:
            Sequence(Wait(2.0), Func(next_song)).start()
            return task.done
    return task.cont

def next_song():
    global music
    global current_song
    current_song += 1
    taskMgr.remove('watchThisSong')
    if music:
        music.stop()
        music = None
    print 'Now recording song: ' + str(FILE_LIST[current_song])
    SendKeys.SendKeys(START_KEY)
    music = base.loadMusic(str(FILE_LIST[current_song]))
    base.playMusic(music)
    taskMgr.doMethodLater(2.0, watch_song, 'watchThisSong')

VIDEO_PATH = ''
VIDEO_EXTENSION = '.mp4'
VIDEO_FILE_LIST = glob.glob(VIDEO_PATH + '*' + VIDEO_EXTENSION)

record = False

def rename_next_song():
    global current_song
    current_song += 1
    print 'Now renaming song: ' + str(VIDEO_FILE_LIST[current_song])
    print 'Renaming to: ' + str(FILE_LIST[current_song])
    path, file_name = FILE_LIST[current_song].split('\\')
    name, extension = file_name.split('.')
    os.rename(VIDEO_FILE_LIST[current_song], name + VIDEO_EXTENSION)

if record:
    next_song()
else:
    rename_next_song()

base.run()

########################################
# Filename: ScreenshotHandler.py
# Created by: DecodedLogic (19Apr16)
########################################
# System used to combat problems that occur when taking
# screenshots in the same thread as everything else is running in.

from datetime import datetime
from pandac.PandaModules import Filename
from direct.interval.IntervalGlobal import Sequence, Wait, Func
import threading
import os

FILEPATH = 'screenshots/'
flashSeq = Sequence()

flashSfx = None

# Let's make sure the screenshots directory exists.
if not os.path.exists(FILEPATH[:-1]):
    os.makedirs(FILEPATH[:-1])

def __doEffects():
    global flashSfx
    if not flashSfx:
        flashSfx = base.loadSfx('phase_4/audio/sfx/Photo_shutter.ogg')
    
    flashSeq = Sequence(
        Func(flashSfx.play),
        Func(base.transitions.setFadeColor, 1, 1, 1),
        Func(base.transitions.fadeOut, 0.1),
        Wait(0.1),
        Func(base.transitions.fadeIn, 0.1),
        Wait(0.1),
        Func(base.transitions.setFadeColor, 0, 0, 0),
    )
    flashSeq.start()

def __saveScreenshot(shot):
    now = datetime.now().strftime(FILEPATH + 'screenshot-%a-%b-%d-%Y-%I-%M-%S-%f')
    shot.write(Filename(now + '.jpeg'))
    return

def __takeScreenshot():
    shot = base.win.getScreenshot()
    thread = threading.Thread(target = __saveScreenshot, args = (shot,))
    thread.start()
    __doEffects()
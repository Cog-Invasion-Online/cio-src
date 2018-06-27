"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIStart.py
@author Brian Lach
@date June 17, 2014

@desc This is the starting point for the game. It initializes a ton of stuff.

"""

from panda3d.core import PandaSystem
from panda3d.core import Thread, loadPrcFile, loadPrcFileData, CollisionTraverser, CullBinManager
from panda3d.core import ConfigVariableDouble
#from panda3d.core import PStatClient, WindowProperties

import Logger
logger = Logger.Starter()
logger.startNotifyLogging()

from direct.directnotify.DirectNotifyGlobal import directNotify
notify = directNotify.newCategory("CIStart")
notify.setInfo(True)

notify.info("Starting the game.")

import os, sys
import datetime

class game:
    name = 'coginvasion'
    process = 'client'
    serverAddress = os.environ.get("GAME_SERVER")
    resourceEncryptionPwd = "cio-03-06-16_lsphases"
    build = 0
    buildtype = "Dev"
    version = "0.0.0"
    builddate = "{:%B %d, %Y}".format(datetime.datetime.now())
    production = False
    phasedir = './resources/'
    usepipeline = False
    uselighting = True
    userealshadows = False
   
import __builtin__
__builtin__.game = game

try:
    import aes
    import config
    # Config
    prc = config.CONFIG
    iv, key, prc = prc[:16], prc[16:32], prc[32:]
    prc = aes.decrypt(prc, key, iv)
    for line in prc.split('\n'):
        line = line.strip()
        if line:
            loadPrcFileData('coginvasion config', line)
    
    import builddata
    game.build = int(builddata.BUILDNUM)
    game.buildtype = builddata.BUILDTYPE
    game.version = builddata.BUILDVER
    game.builddate = builddata.BUILDDATE
    
    # Load phases from root dir in production
    game.phasedir = './'
    game.production = True
    
    notify.info("Running production")
    
except:
    loadPrcFile('config/Confauto.prc')
    loadPrcFile('config/config_client.prc')

    if game.usepipeline:
        sys.path.insert(0, "./renderpipeline")
    
    # Load phases from resoures folder in dev mode
    loadPrcFileData("", "model-path ./resources") # Don't require mounting of phases
    game.phasedir = './resources/'
    game.production = False
    notify.info("Running dev")

notify.info("Version {0} (Build {1} : {2})".format(game.version, game.build, game.buildtype))
notify.info("Phase dir: " + game.phasedir)

from src.coginvasion.manager.SettingsManager import SettingsManager
jsonfile = "settings.json"
notify.info("Reading settings file " + jsonfile)
sm = SettingsManager()
from src.coginvasion.globals import CIGlobals
CIGlobals.SettingsMgr = sm
sm.loadFile(jsonfile)
notify.info("Applying pre settings")
sm.applyPreSettings()

from CIBase import CIBase
base = CIBase()
base.loader.destroy()

notify.info("Applying post settings")
sm.applySettings()

from CogInvasionLoader import CogInvasionLoader
base.loader = CogInvasionLoader(base)
__builtin__.loader = base.loader

# Let's load up our multifiles
base.loader.mountMultifiles(sm.getSetting("resourcepack"))

base.initStuff()

notify.info("Using Panda3D version {0}".format(PandaSystem.getVersionString()))
notify.info("True threading: " + str(Thread.isTrueThreads()))

sm.maybeFixAA()
base.setFrameRateMeter(sm.getSetting("fps"))

# Use our shader generator extension
#import ccoginvasion
#shGen = ccoginvasion.CIShaderGenerator(base.win.getGsg(), base.win)
#base.win.getGsg().setShaderGenerator(shGen)

base.cTrav = CollisionTraverser()

#import AnisotropicFiltering
#AnisotropicFiltering.startApplying()

display = base.config.GetString('load-display')
audio = base.config.GetString('audio-library-name').replace('p3', '').replace('_audio', '')

if display == 'pandagl':
    display = 'OpenGL'
elif 'pandadx' in display:
    display = 'DirectX %s' % (str(display.replace('pandadx', '')))
else:
    display = 'unknown'
notify.info('Using %s graphics library.' % display)

if audio == 'miles':
    audio = 'Miles'
elif audio == 'fmod':
    audio = 'FMOD'
elif audio == 'openal':
    audio = 'OpenAL'

notify.info('Using %s audio library.' % audio)

# Define all of the admin commands.
from src.coginvasion.distributed.AdminCommands import *

from direct.gui import DirectGuiGlobals

from src.coginvasion.base import ScreenshotHandler

base.graphicsEngine.setDefaultLoader(base.loader.loader)
cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
if not game.userealshadows:
    cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
cbm.addBin('gsg-popup', CullBinManager.BTFixed, 70)
base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
base.disableMouse()
base.enableParticles()
base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
base.transitions.IrisModelName = "phase_3/models/misc/iris.bam"
base.transitions.FadeModelName = "phase_3/models/misc/fade.bam"
base.accept(base.inputStore.TakeScreenshot, ScreenshotHandler.__takeScreenshot)

if base.win is None:
    notify.warning("Unable to open window; aborting.")
    sys.exit()
else:
    notify.info("Successfully opened window.")
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)

DirectGuiGlobals.setDefaultFontFunc(CIGlobals.getToonFont)
DirectGuiGlobals.setDefaultFont(CIGlobals.getToonFont())
DirectGuiGlobals.setDefaultRolloverSound(loader.loadSfx("phase_3/audio/sfx/GUI_rollover.ogg"))
DirectGuiGlobals.setDefaultClickSound(loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.ogg"))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel("phase_3/models/gui/dialog_box_gui.bam"))

from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.margins.MarginManager import MarginManager
from src.coginvasion.globals import ChatGlobals

ChatGlobals.loadWhiteListData()
NametagGlobals.setMe(base.cam)
NametagGlobals.setCardModel('phase_3/models/props/panel.bam')
NametagGlobals.setArrowModel('phase_3/models/props/arrow.bam')
NametagGlobals.setChatBalloon3dModel('phase_3/models/props/chatbox.bam')
NametagGlobals.setChatBalloon2dModel('phase_3/models/props/chatbox_noarrow.bam')
NametagGlobals.setThoughtBalloonModel('phase_3/models/props/chatbox_thought_cutout.bam')
chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui.bam')
NametagGlobals.setPageButton(chatButtonGui.find('**/Horiz_Arrow_UP'), chatButtonGui.find('**/Horiz_Arrow_DN'),
                             chatButtonGui.find('**/Horiz_Arrow_Rllvr'), chatButtonGui.find('**/Horiz_Arrow_UP'))
NametagGlobals.setQuitButton(chatButtonGui.find('**/CloseBtn_UP'), chatButtonGui.find('**/CloseBtn_DN'),
                             chatButtonGui.find('**/CloseBtn_Rllvr'), chatButtonGui.find('**/CloseBtn_UP'))
soundRlvr = DirectGuiGlobals.getDefaultRolloverSound()
NametagGlobals.setRolloverSound(soundRlvr)
soundClick = DirectGuiGlobals.getDefaultClickSound()
NametagGlobals.setClickSound(soundClick)

base.marginManager = MarginManager()
base.margins = aspect2d.attachNewNode(base.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
base.leftCells = [
    base.marginManager.addCell(0.1, -0.6, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.0, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.4, base.a2dTopLeft)
]
base.bottomCells = [
    base.marginManager.addCell(0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-1.0, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(1.0, 0.1, base.a2dBottomCenter)
]
base.rightCells = [
    base.marginManager.addCell(-0.1, -0.6, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.0, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.4, base.a2dTopRight)
]

base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
base.mouseWatcherNode.setButtonUpPattern('button-up-%r')

def maybeDoSomethingWithMusic(condition):
    # 0 = paused
    # 1 = restarted
    music = sm.getSetting("music")
    if music:
        base.enableMusic(condition)

def handleMusicEnabled():
    if not hasattr(base, 'cr'):
        return
        
    if base.music is not None:
        base.music.play()

base.accept("PandaPaused", maybeDoSomethingWithMusic, [0])
base.accept("PandaRestarted", maybeDoSomethingWithMusic, [1])
base.accept('MusicEnabled', handleMusicEnabled)

def doneInitLoad():
    notify.info("Initial game load finished.")
    from src.coginvasion.distributed import CogInvasionClientRepository
    base.cr = CogInvasionClientRepository.CogInvasionClientRepository("ver-" + game.version)

notify.info("Starting initial game load...")
from InitialLoad import InitialLoad
il = InitialLoad(doneInitLoad)

from src.coginvasion.base import MusicCache
print "Precaching music..."
MusicCache.precacheMusic()

base.playMusic(CIGlobals.getThemeSong())
il.load()

base.run()

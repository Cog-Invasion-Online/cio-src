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

from src.coginvasion.base.Metadata import Metadata
import __builtin__
__builtin__.metadata = Metadata()

import sys

if metadata.IS_PRODUCTION:
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
    notify.info('Running Production')
else:
    loadPrcFile('config/Confauto.prc')
    loadPrcFile('config/config_client.prc')
    
    loadPrcFileData('', 'model-path ./resources') # Don't require mounting of phases
    notify.info('Running Development Environment')
    
notify.info(metadata.getBuildInformation())
notify.info('Phase directory: {0}'.format(metadata.PHASE_DIRECTORY))

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

notify.info("Applying post settings")
sm.applySettings()

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
import src.coginvasion.distributed.AdminCommands

from direct.gui import DirectGuiGlobals

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
    base.cr = CogInvasionClientRepository.CogInvasionClientRepository("ver-" + metadata.VERSION)

notify.info("Starting initial game load...")
from InitialLoad import InitialLoad
il = InitialLoad(doneInitLoad)

from src.coginvasion.base import MusicCache
print "Precaching music..."
MusicCache.precacheMusic()

base.playMusic(CIGlobals.getThemeSong())
il.load()

base.run()

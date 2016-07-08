########################################
# Filename: CIStart.py
# Created by: blach (17Jun14)
########################################

from panda3d.core import Multifile, Filename, VirtualFileSystem, PandaSystem
from panda3d.core import Thread, loadPrcFile, loadPrcFileData, CollisionTraverser, CullBinManager
from panda3d.core import ConfigVariableDouble, PStatClient

import __builtin__
import os, sys

vfs = VirtualFileSystem.getGlobalPtr()

phases = ['phase_3', 'phase_3.5', 'phase_4', 'phase_5', 'phase_5.5', 'phase_6', 'phase_7', 'phase_8', 'phase_9',
    'phase_10', 'phase_11', 'phase_12', 'phase_13', 'phase_0', 'phase_14', 'tournament_music']
packExtensions = ['.jpg', '.jpeg', '.png', '.ogg', '.rgb', '.mid']

for phase in phases:
    mf = Multifile()
    mf.setEncryptionPassword('cio-03-06-16_lsphases')
    mf.openReadWrite(Filename(phase + '.mf'))
    packMf = None

    if os.path.exists('resourcepack/%s.mf' % phase):
        # Let's remove the unneeded files.
        for subFile in mf.getSubfileNames():
            ext = os.path.splitext(subFile)[1]
            if ext in packExtensions:
                mf.removeSubfile(subFile)

        packMf = Multifile()
        packMf.openReadWrite(Filename('resourcepack/%s.mf' % phase))

        # Let's remove all the default files.
        for subFile in packMf.getSubfileNames():
            ext = os.path.splitext(subFile)[1]
            if ext not in packExtensions:
                packMf.removeSubfile(subFile)
    vfs.mount(mf, '.', 0)
    print 'Mounted %s from default.' % phase
    if packMf:
        vfs.mount(packMf, '.', 0)
        print 'Mounted %s from resource pack.' % phase

import Logger
Logger.Starter()

from lib.coginvasion.manager.SettingsManager import SettingsManager
jsonfile = "settings.json"
print "CIStart: Reading settings file " + jsonfile
sm = SettingsManager()

class game:
    name = 'coginvasion'
    process = 'client'
    version = os.environ.get("GAME_VERSION")
    serverAddress = os.environ.get("GAME_SERVER")


__builtin__.game = game()

print "CIStart: Starting the game."
print "CIStart: Using Panda3D version {0}".format(PandaSystem.getVersionString())
print 'CIStart: True threading: ' + str(Thread.isTrueThreads())

try:
    import aes
    import niraidata
    # Config
    prc = niraidata.CONFIG
    iv, key, prc = prc[:16], prc[16:32], prc[32:]
    prc = aes.decrypt(prc, key, iv)
    for line in prc.split('\n'):
        line = line.strip()
        if line:
            loadPrcFileData('coginvasion config', line)
    print "CIStart: Running production"
except:
    loadPrcFile('config/Confauto.prc')
    loadPrcFile('config/config_client.prc')
    print "CIStart: Running dev"
sm.maybeFixAA()

from direct.showbase.ShowBase import ShowBase
base = ShowBase()
base.cTrav = CollisionTraverser()

display = base.config.GetString('load-display')
audio = base.config.GetString('audio-library-name').replace('p3', '').replace('_audio', '')

if display == 'pandagl':
    display = 'OpenGL'
elif 'pandadx' in display:
    display = 'DirectX %s' % (str(display.replace('pandadx', '')))
else:
    display = 'unknown'
print 'CIStart: Using %s graphics library.' % display

if audio == 'miles':
    audio = 'Miles'
elif audio == 'fmod':
    audio = 'FMOD'
elif audio == 'openal':
    audio = 'OpenAL'
print 'CIStart: Using %s audio library.' % audio

from direct.gui import DirectGuiGlobals

from lib.coginvasion.base import ScreenshotHandler
import CogInvasionLoader

base.loader = CogInvasionLoader.CogInvasionLoader(base)
base.graphicsEngine.setDefaultLoader(base.loader.loader)
__builtin__.loader = base.loader
from lib.coginvasion.globals import CIGlobals
cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
base.disableMouse()
base.enableParticles()
base.musicManager.setVolume(0.65)
base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
base.transitions.IrisModelName = "phase_3/models/misc/iris.bam"
base.transitions.FadeModelName = "phase_3/models/misc/fade.bam"
base.accept('f9', ScreenshotHandler.__takeScreenshot)

print "CIStart: Setting display preferences..."
sm.applySettings(jsonfile)
if base.win == None:
    print "CIStart: Unable to open window; aborting."
    sys.exit()
else:
    print "CIStart: Successfully opened window."
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)

DirectGuiGlobals.setDefaultFontFunc(CIGlobals.getToonFont)
DirectGuiGlobals.setDefaultFont(CIGlobals.getToonFont())
DirectGuiGlobals.setDefaultRolloverSound(loader.loadSfx("phase_3/audio/sfx/GUI_rollover.ogg"))
DirectGuiGlobals.setDefaultClickSound(loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.ogg"))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel("phase_3/models/gui/dialog_box_gui.bam"))

from lib.coginvasion.nametag import NametagGlobals
from lib.coginvasion.margins.MarginManager import MarginManager
from lib.coginvasion.globals import ChatGlobals

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

# HACK: I don't feel like making a new file that inherits from ShowBase so I'm just going to do this...
def setCellsActive(cells, active):
    for cell in cells:
        cell.setActive(active)
    base.marginManager.reorganize()
base.setCellsActive = setCellsActive

def windowEvent(win):
    ShowBase.windowEvent(base, win)
    base.marginManager.updateMarginVisibles()
base.windowEvent = windowEvent

base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
base.mouseWatcherNode.setButtonUpPattern('button-up-%r')

def maybeDoSomethingWithMusic(condition):
    # 0 = paused
    # 1 = restarted
    _, _, _, music, _, _, _, _, _ = sm.getSettings(jsonfile)
    if music:
        base.enableMusic(condition)

def handleMusicEnabled():
    if base.cr.music is not None:
        base.cr.music.play()

base.accept("PandaPaused", maybeDoSomethingWithMusic, [0])
base.accept("PandaRestarted", maybeDoSomethingWithMusic, [1])
base.accept('MusicEnabled', handleMusicEnabled)

def doneInitLoad():
    print "CIStart: Initial game load finished."
    from lib.coginvasion.distributed import CogInvasionClientRepository
    base.cr = CogInvasionClientRepository.CogInvasionClientRepository(music, "ver-" + game.version)

print "CIStart: Starting initial game load..."
from InitialLoad import InitialLoad
il = InitialLoad(doneInitLoad)
music = base.loadMusic(CIGlobals.getThemeSong())
base.playMusic(music, looping = 1, volume = 0.5)
il.load()

base.run()

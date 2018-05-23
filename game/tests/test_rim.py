from panda3d.core import *
loadPrcFile("config/Confauto.prc")
loadPrcFile("config/config_client.prc")

class game:
    process = 'client'
    phasedir = './resources'
    userealshadows = False
import __builtin__
__builtin__.game = game

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("resources/phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_14.mf"), ".", VirtualFileSystem.MFReadOnly)

from direct.showbase.ShowBase import ShowBase
base = ShowBase()

from direct.showbase.Audio3DManager import Audio3DManager
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
base.audio3d.setDistanceFactor(25)
base.audio3d.setDropOffFactor(0.025)

from src.coginvasion.manager.SettingsManager import SettingsManager

sm = SettingsManager()
sm.loadFile("settings.json")

sm.maybeFixAA()

sm.applySettings()
from src.coginvasion.globals import CIGlobals
CIGlobals.SettingsMgr = sm

base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()
base.lifter = CollisionHandlerFloor()
base.pusher = CollisionHandlerPusher()
base.queue = CollisionHandlerQueue()
from direct.distributed.ClientRepository import ClientRepository
base.cr = ClientRepository([])
base.cr.isShowingPlayerIds = False

amb = AmbientLight("amb")
amb.setColor(Vec4(172 / 255.0, 196 / 255.0, 202 / 255.0, 1.0))
#amb.setColor(Vec4(0.5))
ambNp = render.attachNewNode(amb)
render.setLight(ambNp)

dir = DirectionalLight("dir")
dir.setColor(Vec4(252 / 255.0, 239 / 255.0, 209 / 255.0, 1.0))
#dir.setColor(Vec4(1))
#dir.setDirection(Vec3(0.5, 0.5, -0.8))
#dir.showFrustum()
dir.getLens().setFilmSize(500, 500)
dirNp = render.attachNewNode(dir)
dirNp.setHpr(-45, -75, 0)
render.setLight(dirNp)

lightwarps = ["phase_3/maps/toon_lightwarp.jpg", "phase_3/maps/toon_lightwarp_2.jpg", "test_lightwarp.png",
              "phase_3/maps/toon_lightwarp_cartoon.jpg", "phase_3/maps/toon_lightwarp_dramatic.jpg",
              "phase_3/maps/toon_lightwarp_bright.jpg"]

from src.coginvasion.toon.Toon import Toon

toonRoot = render.attachNewNode('toonRoot')
toon = Toon(base.cr)
toon.setDNAStrand("00/01/05/19/01/19/01/19/13/05/27/27/00", makeTag = 0)
toon.reparentTo(toonRoot)
toon.loop("neutral")
#toonRoot.setMaterial(CIGlobals.getCharacterMaterial(specular = (0, 0, 0, 0), lightwarp = lightwarps[i]))
toon.setX(0)
tn = TextNode('lightwarp_display')
tn.setText("No Lightwarp")
#tn.setTextDecal(True)
tn.setTextColor((1, 1, 1, 1))
tn.setAlign(TextNode.ACenter)
tnnp = toon.attachNewNode(tn)
tnnp.setZ(4.3)
tnnp.setBillboardAxis()
tnnp.setScale(0.2)

lw_idx = -1
def nextMat():
    global lw_idx
    lw_idx += 1
    if lw_idx < len(lightwarps):
        toon.setMaterial(CIGlobals.getCharacterMaterial(specular = (0, 0, 0, 0), lightwarp = lightwarps[lw_idx]))
        tn.setText(Filename(lightwarps[lw_idx]).getBasename())
    else:
        lw_idx = -1
        toon.setMaterial(CIGlobals.getCharacterMaterial(specular = (0, 0, 0, 0), lightwarp = None))
        tn.setText("No Lightwarp")

def scrollTask(task):
    nextMat()
    task.delayTime = 0.7
    return task.again

taskMgr.doMethodLater(1.5, scrollTask, "scrollTask")

render.setShaderAuto()
base.disableMouse()
camera.setPos(-4, 13, 3)
camera.lookAt(toon, 0, 0, 3)
base.run()
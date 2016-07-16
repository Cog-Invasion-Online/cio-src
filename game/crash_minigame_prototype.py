from lib.coginvasion.standalone.StandaloneToon import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

base.transitions.fadeScreen(1.0)

base.disableMouse()

base.localAvatar.disableAvatarControls()
base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.setAnimState('off')

class Jellybean(NodePath, DirectObject):
    notify = directNotify.newCategory("Jellybean")
    
    def __init__(self, gui, collectable = True):
        NodePath.__init__(self, 'jellybean')
        
        self.gui = gui

        self.mdl = loader.loadModel("phase_4/models/props/jellybean4.bam")
        self.mdl.setColor(VBase4(0.3, 0.3, 1.0, 1.0))
        self.mdl.flattenLight()
        self.mdl.reparentTo(self)
        self.mdl.setScale(3.0)
        self.mdl.setZ(1.0)
        
        self.jbCollNP = None
        
        self.spinIval = None
        
        self.pickupIval = None
        
        self.collectable = collectable
        if self.collectable:
            self.__initialiseCollisions()
            self.spinIval = LerpHprInterval(
                self,
                duration = 0.5,
                hpr = Vec3(360, 0, 0),
                startHpr = Vec3(0, 0, 0)
            )
            self.spinIval.loop()
            
    def getCollNodeName(self):
        return 'jbnode' + str(id(self))
            
    def __initialiseCollisions(self):
        sphere = CollisionSphere(0, 0, 0, 1)
        sphere.setTangible(0)
        node = CollisionNode(self.getCollNodeName())
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.jbCollNP = self.attachNewNode(node)
        
    def allowPickup(self):
        self.acceptOnce('enter' + self.getCollNodeName(), self.__handleCollision)
        
    def __handleCollision(self, entry):
        print "picked one up"
        self.gui.collectedBean()
        self.wrtReparentTo(camera)
        self.setDepthWrite(1)
        self.setDepthTest(1)
        
        self.pickupIval = LerpPosInterval(
            self,
            duration = 1.0,
            pos = (-3, 8, 1),
            startPos = self.getPos(camera),
        )
        self.pickupIval.setDoneEvent(self.getCollNodeName())
        self.acceptOnce(self.pickupIval.getDoneEvent(), self.__handleMoveToGuiDone)
        self.pickupIval.start()
        
    def __handleMoveToGuiDone(self):
        print "cleanup"
        self.gui.incrementJbs()
        self.cleanup()
        
    def cleanup(self):
        if self.pickupIval:
            self.ignore(self.pickupIval.getDoneEvent())
            self.pickupIval.finish()
            self.pickupIval = None
        if self.spinIval:
            self.spinIval.finish()
            self.spinIval = None
        if self.jbCollNP:
            self.jbCollNP.removeNode()
            self.jbCollNP = None
        if self.mdl:
            self.mdl.removeNode()
            self.mdl = None
        self.collectable = None
        self.gui = None

class CrashGUIItem(DirectFrame):
    notify = directNotify.newCategory('CrashGUIItem')
    
    DownZ = -0.25
    UpZ = 0.5
    
    def __init__(self, visItem, visScale, frameX, visX, textX, textZ, textScale, spins = False):
        DirectFrame.__init__(self, parent = base.a2dTopCenter, pos = (frameX, 0, self.UpZ))
        
        self.frameX = frameX
        
        self.item = visItem
        self.item.flattenLight()
        self.item.setDepthWrite(1)
        self.item.setDepthTest(1)
        self.item.setScale(visScale)
        self.item.setX(visX)
        self.item.reparentTo(self)
        
        self.spinIval = None
        if spins:
            self.spinIval = LerpHprInterval(
                self.item,
                duration = 0.5,
                hpr = Vec3(360, 0, 0),
                startHpr = Vec3(0, 0, 0)
            )
            self.spinIval.loop()
        
        self.text = OnscreenText(parent = self, pos = (textX, textZ, 0),
            scale = textScale, shadow = (0, 0, 0, 1), fg = (0.5, 0.5, 1.0, 1.0))
            
        self.fsm = ClassicFSM(
            "ItemFSM",
            [
                State('off', self.enterOff, self.exitOff),
                State('up', self.enterUp, self.exitUp),
                State('up2down', self.enterUp2Down, self.exitUp2Down),
                State('down', self.enterDown, self.exitDown),
                State('down2up', self.enterDown2Up, self.exitDown2Up)
            ],
            "up",
            "off"
        ); self.fsm.enterInitialState()
        
        self.initialiseoptions(CrashGUIItem)
        
    def taskName(self, name):
        return name + "-" + str(id(self))
        
    def enterOff(self):
        pass
        
    def exitOff(self):
        pass
        
    def enterUp(self):
        self.setZ(self.UpZ)
        
    def exitUp(self):
        pass
        
    def enterUp2Down(self):
        self.ival = LerpPosInterval(
            self,
            duration = 0.5,
            pos = (self.frameX, 0, self.DownZ),
            startPos = (self.frameX, 0, self.UpZ),
            name = self.taskName('up2downival'))
        self.ival.setDoneEvent(self.ival.getName())
        self.acceptOnce(self.ival.getDoneEvent(), self.__up2DownDone)
        self.ival.start()
    
    def __up2DownDone(self):
        self.fsm.request('down')
        
    def exitUp2Down(self):
        self.ignore(self.ival.getDoneEvent())
        self.ival.finish()
        del self.ival
        
    def enterDown(self):
        self.setZ(self.DownZ)
        downTime = 3.0
        taskMgr.doMethodLater(downTime, self.__downTask, self.taskName('downTask'))
        
    def __downTask(self, task):
        self.fsm.request('down2up')
        return task.done
        
    def exitDown(self):
        taskMgr.remove(self.taskName('downTask'))
        
    def enterDown2Up(self):
        self.ival = LerpPosInterval(
            self,
            duration = 0.5,
            pos = (self.frameX, 0, self.UpZ),
            startPos = (self.frameX, 0, self.DownZ),
            name = self.taskName('down2upival'))
        self.ival.setDoneEvent(self.ival.getName())
        self.acceptOnce(self.ival.getDoneEvent(), self.__down2UpDone)
        self.ival.start()
    
    def __down2UpDone(self):
        self.fsm.request('up')
        
    def exitDown2Up(self):
        self.ignore(self.ival.getDoneEvent())
        self.ival.finish()
        del self.ival
        
    def setTextText(self, text):
        self.text.setText(text)
        
    def show(self):
        if self.fsm.getCurrentState().getName() in ['up', 'down2up']:
            self.fsm.request('up2down')
        elif self.fsm.getCurrentState().getName() == 'down':
            taskMgr.remove(self.taskName('downTask'))
            self.enterDown()

class CrashGUI:
    notify = directNotify.newCategory('CrashGUI')
    
    def __init__(self):
        self.pickupSound = base.loadSfx('phase_4/audio/sfx/MG_maze_pickup.ogg')
        
        jb = loader.loadModel('phase_4/models/props/jellybean4.bam')
        jb.setColor(VBase4(0.3, 0.3, 1.0, 1.0))
        self.jbItem = CrashGUIItem(jb, 1.0, -1.1, 0, 0.2, -0.05, 0.25, True)
        self.jbItem.setTextText("0")
        
        self.frames = [self.jbItem]
        self.jbs = []
        
        self.jbsCollected = 0
        
        jbTrans = ((5, 0, 0), (5, 1.5, 0), (5, 3.0, 0), (5, 4.5, 0),
            (62.62, 11.89, 0), (62.62, 9.36, 0), (62.62, 6, 0),
            (62.62, 2.5, 0), (-0.35, -49.99, 0), (-4.75, -48.72, 0),
            (-0.96, -44.61, 0), (-7.68, -42.18, 0), (-52.42, 0.30, 0),
            (-51.60, -4.12, 0), (-51.60, -8.17, 0), (-50.63, -13.01, 0))
            
        for trans in jbTrans:
            jb = Jellybean(self)
            jb.reparentTo(render)
            jb.setPos(trans)
            jb.allowPickup()
            self.jbs.append(jb)
            
        #self.jbs[len(self.jbs) - 1].place()
            
    def collectedBean(self):
        base.playSfx(self.pickupSound)
        self.jbItem.show()
        
    def incrementJbs(self):
        self.jbsCollected += 1
        self.jbItem.setTextText(str(self.jbsCollected))
        
    def showAll(self):
        for frame in self.frames:
            frame.show()
            
from lib.coginvasion.cogtropolis.NURBSMopath import NURBSMopath

SPPlatform = 56
            
class Game:
    
    def __init__(self):
        self.gui = None
        self.mopath = None
        self.platform = None
        self.platformNode = None
        
        self.music = base.loadMusic('phase_4/audio/bgm/MG_Crash.ogg')

        self.area = loader.loadModel('phase_4/models/minigames/crash_test_area.egg')
        self.area.reparentTo(render)
        self.area.find('**/ground').setBin('ground', 18)
        
        base.acceptOnce('s', self.start)
    
    def teleInDone(self):
        base.localAvatar.setAnimState('Happy')
        base.localAvatar.enableAvatarControls()
        base.localAvatar.startTrackAnimToSpeed()
        
    def __handleSteppedOnPlatform(self, entry):
        curve = self.area.find('**/platform_path')
        #base.localAvatar.disableAvatarControls()
        self.platformNode.ls()
        base.localAvatar.reparentTo(self.platformNode)
        base.localAvatar.setPos(0, 0, 0)
        mopath = NURBSMopath(curve)
        mopath.play(self.platformNode, duration = 10.0, rotate = False)

    def start(self):
        
        base.localAvatar.setAnimState('teleportIn', callback = self.teleInDone)
        base.transitions.fadeIn(0.2)
        base.localAvatar.smartCamera.setCameraPositionByIndex(4)
        base.playMusic(self.music, looping = 1, volume = 0.7)
        self.gui = CrashGUI()
        self.gui.showAll()
        
        self.platformNode = loader.loadModel('crash_platform.bam')
        self.platformNode.reparentTo(render)
        self.platformNode.setPosHpr(1.23, 66.51, 0, 90, 0, 0)
        
        self.area.ls()
        self.area.find('**/platform').removeNode()
        self.area.find('**/platform_coll').removeNode()
        
        base.acceptOnce('enterplatform_coll', self.__handleSteppedOnPlatform)

game = Game()

base.run()

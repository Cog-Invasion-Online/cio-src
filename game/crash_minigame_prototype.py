from lib.coginvasion.standalone.StandaloneToon import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

base.transitions.fadeScreen(1.0)

music = base.loadMusic('phase_4/audio/bgm/MG_Crash.mid')

base.disableMouse()

base.localAvatar.disableAvatarControls()
base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()
base.localAvatar.setAnimState('off')

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

class CrashGUI:
    notify = directNotify.newCategory('CrashGUI')
    
    def __init__(self):
        jb = loader.loadModel('phase_4/models/props/jellybean4.bam')
        jb.setColor(VBase4(0.3, 0.3, 1.0, 1.0))
        jbItem = CrashGUIItem(jb, 1.0, -1.1, 0, 0.2, -0.05, 0.25, True)
        jbItem.setTextText("0")
        
        self.frames = [jbItem]
        
    def showAll(self):
        for frame in self.frames:
            frame.show()
        
gui = None
    
def teleInDone():
    base.localAvatar.setAnimState('Happy')
    base.localAvatar.enableAvatarControls()
    base.localAvatar.startTrackAnimToSpeed()

def start():
    global gui
    base.localAvatar.setAnimState('teleportIn', callback = teleInDone)
    base.transitions.fadeIn(0.2)
    base.localAvatar.smartCamera.setCameraPositionByIndex(4)
    base.playMusic(music, looping = 1, volume = 0.8)
    gui = CrashGUI()
    gui.showAll()
    
Sequence(Wait(0.5), Func(start)).start()

base.run()

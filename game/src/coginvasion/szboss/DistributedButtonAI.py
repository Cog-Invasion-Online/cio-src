from panda3d.core import Point3

from DistributedEntityAI import DistributedEntityAI
from direct.fsm.FSM import FSM

class DistributedButtonAI(DistributedEntityAI, FSM):

    PressWhenLocked = 2
    StartsPressed = 32
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        FSM.__init__(self, 'DButtonAI')
        self.state = 0
        self.locked = 0
        self.wait = 0.0
        self.moveDuration = 0.0
        
    def delete(self):
        self.request('Off')
        self.state = None
        self.locked = None
        self.wait = None
        self.moveDuration = None
        DistributedEntityAI.delete(self)
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        if self.spawnflags & self.StartsPressed:
            self.b_setState(2)
        
    def __btnMoveDone(self, nextState, task):
        self.b_setState(nextState)
        return task.done
        
    def enterDepressed(self):
        pass
        
    def exitDepressed(self):
        pass
        
    def enterPressing(self):
        taskMgr.doMethodLater(self.moveDuration, self.__btnMoveDone, name = self.uniqueName('btnpresstask'),
                              extraArgs = [2], appendTask = True)
                              
    def exitPressing(self):
        taskMgr.remove(self.uniqueName('btnpresstask'))
        
    def enterPressed(self):
        if not self.locked:
            self.dispatchOutput("OnPress")
            
        if self.wait != -1:
            taskMgr.doMethodLater(self.wait, self.__btnMoveDone, name = self.uniqueName('btnpressedtask'),
                                  extraArgs = [3], appendTask = True)
                                  
    def exitPressed(self):
        taskMgr.remove(self.uniqueName('btnpressedtask'))
        
    def enterDepressing(self):
        taskMgr.doMethodLater(self.moveDuration, self.__btnMoveDone, name = self.uniqueName('btndepresstask'),
                              extraArgs = [0], appendTask = True)
                              
    def exitDepressing(self):
        taskMgr.remove(self.uniqueName('btndepresstask'))
        
    def loadEntityValues(self):
        self.wait = self.getEntityValueInt("wait")
        moveDir = self.getEntityValueVector("movedir")
        speed = self.getEntityValueFloat("speed")
        self.spawnflags = self.getEntityValueInt("spawnflags")
        
        mins = Point3(0)
        maxs = Point3(0)
        self.bspLoader.getModelBounds(self.bspLoader.extractModelnum(self.entnum), mins, maxs)
        posDelta = maxs - mins
        posDelta.componentwiseMult(moveDir)
        self.moveDuration = (posDelta.length() * 16.0) / speed
    
    def getState(self):
        return self.state
        
    def setState(self, state):
        self.state = state
        if state == 0:
            self.request('Depressed')
        elif state == 1:
            self.request('Pressing')
        elif state == 2:
            self.request('Pressed')
        elif state == 3:
            self.request('Depressing')
            
    def b_setState(self, state):
        self.sendUpdate('setState', [state])
        self.setState(state)
        
    def requestPress(self):
        if self.state == 0:
            if not self.locked or (self.locked and self.spawnflags & self.PressWhenLocked):
                self.b_setState(1)
            
    def Unlock(self):
        self.locked = 0
    
    def Lock(self):
        self.locked = 1
        
    def Press(self):
        self.requestPress()
        
    def Depress(self):
        self.b_setState(3)

from panda3d.core import Point3

from direct.fsm.FSM import FSM

from DistributedEntityAI import DistributedEntityAI

DOORSTATE_CLOSED = 0
DOORSTATE_OPENING = 1
DOORSTATE_OPENED = 2
DOORSTATE_CLOSING = 3

class DistributedFuncDoorAI(DistributedEntityAI, FSM):

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        FSM.__init__(self, 'FuncDoorAI')
        self.state = DOORSTATE_CLOSED
        self.wait = 0.0
        self.moveDuration = 0.0
        
    def requestOpen(self):
        if self.state == DOORSTATE_CLOSED:
            print "Got request to open door, doing it!"
            self.Open()
        
    def Open(self):
        self.b_setDoorState(DOORSTATE_OPENING)
        
    def Close(self):
        self.b_setDoorState(DOORSTATE_CLOSING)
        
    def loadEntityValues(self):
        self.wait = self.bspLoader.getEntityValueInt(self.entnum, "wait")
        moveDir = self.bspLoader.getEntityValueVector(self.entnum, "movedir")
        speed = self.bspLoader.getEntityValueFloat(self.entnum, "speed")
        
        mins = Point3(0)
        maxs = Point3(0)
        self.bspLoader.getModelBounds(self.bspLoader.extractModelnum(self.entnum), mins, maxs)
        posDelta = maxs - mins
        posDelta.componentwiseMult(moveDir)
        self.moveDuration = (posDelta.length() * 16.0) / speed
        
    def setDoorState(self, state):
        self.state = state
        if state == DOORSTATE_CLOSED:
            self.request('Closed')
        elif state == DOORSTATE_OPENING:
            self.request('Opening')
        elif state == DOORSTATE_OPENED:
            self.request('Opened')
        elif state == DOORSTATE_CLOSING:
            self.request('Closing')
            
    def getDoorState(self):
        return self.state
            
    def b_setDoorState(self, state):
        self.sendUpdate('setDoorState', [state])
        self.setDoorState(state)
        
    def enterClosed(self):
        self.dispatchOutput("OnCloseFinish")
        
    def exitClosed(self):
        pass
        
    def enterOpening(self):
        self.dispatchOutput("OnOpenStart")
        taskMgr.doMethodLater(self.moveDuration, self.__doorMoveDone, name = self.uniqueName('doorOpenTask'),
                              extraArgs = [DOORSTATE_OPENED], appendTask = True)
        
    def exitOpening(self):
        taskMgr.remove(self.uniqueName('doorOpenTask'))
        
    def enterClosing(self):
        self.dispatchOutput("OnCloseStart")
        taskMgr.doMethodLater(self.moveDuration, self.__doorMoveDone, name = self.uniqueName('doorCloseTask'),
                              extraArgs = [DOORSTATE_CLOSED], appendTask = True)
    
    def exitClosing(self):
        taskMgr.remove(self.uniqueName('doorCloseTask'))
        
    def enterOpened(self):
        self.dispatchOutput("OnOpenFinish")
        if self.wait != -1:
            taskMgr.doMethodLater(self.wait, self.__doorMoveDone, name = self.uniqueName('doorOpenDone'),
                                  extraArgs = [DOORSTATE_CLOSING], appendTask = True)
        
    def exitOpened(self):
        taskMgr.remove(self.uniqueName('doorOpenDone'))
        
    def __doorMoveDone(self, nextState, task):
        self.b_setDoorState(nextState)
        return task.done
        
    def delete(self):
        self.request('Off')
        self.state = None
        self.moveDuration = None
        self.wait = None
        DistributedEntityAI.delete(self)

from panda3d.core import Point3, Vec3

from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func

from DistributedEntityAI import DistributedEntityAI

DOORSTATE_CLOSED = 0
DOORSTATE_OPENING = 1
DOORSTATE_OPENED = 2
DOORSTATE_CLOSING = 3

class DistributedFuncDoorAI(DistributedEntityAI, FSM):

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        FSM.__init__(self, 'FuncDoorAI')
        self._doorState = DOORSTATE_CLOSED
        self.wait = 0.0
        self.moveDuration = 0.0
        self.speed = 0.0
        self.moveDir = Vec3(0)
        self.origin = Point3(0)
        self.moveIval = None
        self.mins = Point3(0)
        self.maxs = Point3(0)
        self.loopMoveSound = False
        self.locked = False
        
    def filterOpened(self, request, args):
        if request == 'Closing':
            return (request,) + args
        return None
        
    def filterClosed(self, request, args):
        if request == 'Opening':
            return (request,) + args
        return None
        
    def filterOpening(self, request, args):
        if request in ['Opened', 'Closing']:
            return (request,) + args
        return None
        
    def filterClosing(self, request, args):
        if request in ['Opening', 'Closed']:
            return (request,) + args
        return None
        
    def Lock(self):
        self.locked = True
        
    def Unlock(self):
        self.locked = False
        self.d_playSound("unlocked")

    def playMoveSound(self):
        if self.loopMoveSound:
            self.d_loopSound("movesnd")
        else:
            self.d_playSound("movesnd")

    def stopMoveSound(self):
        self.d_stopSound("movesnd")

    def playStopSound(self):
        self.d_playSound("stopsnd")
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        self.startPosHprBroadcast()

        if self.hasSpawnFlags(1): # starts open
            self.Open()
        if self.hasSpawnFlags(2): # starts locked
            self.Lock()
        
    def getDoorData(self):
        posDelta = self.maxs - self.mins
        posDelta.componentwiseMult(self.moveDir)
        openPos = self.origin + posDelta
        closedPos = self.origin
        duration = (posDelta.length() * 16.0) / self.speed
        
        data = [posDelta, openPos, closedPos, self.origin]
        print data
        
        return [posDelta, openPos, closedPos, duration]
        
    def requestOpen(self):
        if self._doorState == DOORSTATE_CLOSED:
            if self.locked:
                self.d_playSound("locked")
            else:
                self.Open()
        
    def Open(self):
        if self.getDoorState() in [DOORSTATE_OPENED, DOORSTATE_OPENING] or self.locked:
            return
        self.setDoorState(DOORSTATE_OPENING)
        
    def Close(self):
        if self.getDoorState() in [DOORSTATE_CLOSED, DOORSTATE_CLOSING]:
            return
        self.setDoorState(DOORSTATE_CLOSING)
        
    def loadEntityValues(self):
        self.wait = self.getEntityValueFloat("wait")
        self.moveDir = self.getEntityValueVector("movedir")
        self.speed = self.getEntityValueFloat("speed")
        self.cEntity.getModelBounds(self.mins, self.maxs)
        self.origin = self.cEntity.getModelNp().getPos()
        self.loopMoveSound = self.getEntityValueBool("loop_movesnd")

    def setDoorState(self, state):
        if state == self._doorState:
            return
            
        self._doorState = state
        if state == DOORSTATE_CLOSED:
            self.request('Closed')
        elif state == DOORSTATE_OPENING:
            self.request('Opening')
        elif state == DOORSTATE_OPENED:
            self.request('Opened')
        elif state == DOORSTATE_CLOSING:
            self.request('Closing')
            
    def getDoorState(self):
        return self._doorState
        
    def enterClosed(self):
        self.dispatchOutput("OnCloseFinish")

        self.stopMoveSound()
        self.playStopSound()
        closedPos = self.getDoorData()[2]
        self.setPos(closedPos)
        
    def exitClosed(self):
        pass
        
    def stopMoveIval(self):
        if self.moveIval:
            self.moveIval.pause()
        self.moveIval = None
        
    def enterOpening(self):
        self.dispatchOutput("OnOpenStart")
        
        self.stopMoveIval()
        
        posDelta, openPos, closedPos, duration = self.getDoorData()
            
        self.moveIval = Sequence(Func(self.playMoveSound),
                                 LerpPosInterval(self, pos = openPos, startPos = closedPos,
                                                 duration = duration),
                                 Func(self.setDoorState, DOORSTATE_OPENED))
        
        self.moveIval.start()
        
    def exitOpening(self):
        self.stopMoveIval()
        
    def enterClosing(self):
        self.dispatchOutput("OnCloseStart")
        
        self.stopMoveIval()
            
        posDelta, openPos, closedPos, duration = self.getDoorData()
        
        self.moveIval = Sequence()
        self.moveIval.append(Func(self.playMoveSound))
        self.moveIval.append(LerpPosInterval(self, pos = closedPos, startPos = openPos, duration = duration))
        self.moveIval.append(Func(self.setDoorState, DOORSTATE_CLOSED))
        self.moveIval.start()
    
    def exitClosing(self):
        self.stopMoveIval()
        
    def enterOpened(self):
        self.dispatchOutput("OnOpenFinish")

        self.stopMoveSound()
        self.playStopSound()
        openPos = self.getDoorData()[1]
        self.setPos(openPos)

        if self.wait != -1:
            taskMgr.doMethodLater(self.wait, self.__doorMoveDone, name = self.uniqueName('doorOpenDone'),
                                  extraArgs = [DOORSTATE_CLOSING], appendTask = True)
        
    def exitOpened(self):
        taskMgr.remove(self.uniqueName('doorOpenDone'))
        
    def __doorMoveDone(self, nextState, task):
        self.setDoorState(nextState)
        return task.done
        
    def delete(self):
        self.request('Off')
        self.stopMoveIval()
        self._doorState = None
        self.wait = None
        self.moveDuration = None
        self.speed = None
        self.moveDir = None
        self.origin = None
        self.moveIval = None
        self.mins = None
        self.maxs = None
        self.loopMoveSound = None
        DistributedEntityAI.delete(self)

########################################
# Filename: DistributedPet.py
# Created by: DecodedLogic (25Feb16)
########################################
from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

class DistributedPet(DistributedAvatar):
    
    def __init__(self, cr):
        DistributedAvatar.__init__(self, cr)
        self.owner = None
        self.movementFSM = ClassicFSM('Pet', [
            State('off', self.enterOff, self.exitOff),
            State('forward', self.enterMoveForward, self.exitMoveForward),
            State('backward', self.enterMoveBackward, self.exitMoveBackward),
            State('left', self.enterTurnLeft, self.exitTurnLeft),
            State('right', self.enterTurnRight, self.exitTurnRight)
        ], 'off', 'off')
    
    def enterOff(self):
        pass
    
    def exitOff(self):
        pass
    
    def enterMoveForward(self, ts = 0):
        pass
    
    def exitMoveForward(self):
        pass
    
    def enterMoveBackward(self, ts = 0):
        pass
    
    def exitMoveBackward(self):
        pass
    
    def enterTurnLeft(self, ts = 0):
        pass
    
    def exitTurnLeft(self):
        pass
    
    def enterTurnRight(self, ts = 0):
        pass
    
    def exitTurnRight(self):
        pass

    def setOwner(self, avId):
        avatar = self.cr.doId2do.get(avId)
        if avatar and avatar.__class__.__name__ == 'DistributedPlayerToon':
            self.owner = avatar
            
    def d_setOwner(self, avId):
        self.sendUpdate('setOwner', [avId])
        
    def b_setOwner(self, avId):
        self.setOwner(avId)
        self.d_setOwner(avId)
        
    def isLocalOwner(self):
        return base.localAvatar == self.owner
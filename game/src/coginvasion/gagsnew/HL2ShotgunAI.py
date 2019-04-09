from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from HL2ShotgunShared import HL2ShotgunShared
from BaseHitscanAI import BaseHitscanAI

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_HL2SHOTGUN

class HL2ShotgunAI(BaseHitscanAI, HL2ShotgunShared):

    Name = GagGlobals.HL2Shotgun
    ID = ATTACK_HL2SHOTGUN
    HasClip = True
    AttackRange = 10000
    FireDelay = 0.5
    FriendlyFire = True
    
    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StatePump   :   0.666666666667,
                                   self.StateReload :   0.5,
                                   self.StateBeginReload    :   0.625,
                                   self.StateEndReload  :   0.541666666667,
                                   self.StateFire   :   0.416666666667,
                                   self.StateDblFire    :   0.625,
                                   self.StateDraw   :   0.916666666667})
        self.maxAmmo = 32
        self.ammo = 32
        self.maxClip = 6
        self.clip = 6
        self.needsPump = False

    def shouldGoToNextAction(self, complete):
        return ((complete) or
               (not complete and self.action == self.StatePump and
                self.getActionTime() >= self.FireDelay and self.nextAction == self.StateFire))
                                   
    def determineNextAction(self, completedAction):
        if completedAction in [self.StateFire, self.StateDblFire]:
            if self.clip <= 0 and self.ammo > 0:
                self.needsPump = True
                return self.StateBeginReload
            else:
                return self.StatePump
        elif completedAction == self.StateBeginReload:
            return self.StateReload
        elif completedAction == self.StateReload:
            self.clip += 1
            if self.clip < self.maxClip and self.clip < self.ammo:
                return self.StateReload
            else:
                return self.StateEndReload
        elif completedAction == self.StateEndReload:
            if self.needsPump:
                self.needsPump = False
                return self.StatePump
            else:
                return self.StateIdle
        elif completedAction == self.StateDraw:
            if self.clip <= 0:
                self.needsPump = True
                return self.StateBeginReload
            elif self.needsPump:
                self.needsPump = False
                return self.StatePump
            else:
                return self.StateIdle
                
        return self.StateIdle
        
    def onSetAction(self, action):
        if action == self.StateFire:
            self.takeAmmo(-1)
            self.clip -= 1
            
            self.doTraceAndDamage(1)

        elif action == self.StateDblFire:
            self.takeAmmo(-2)
            self.clip -= 2

            self.doTraceAndDamage(2)

    def canUseSecondary(self):
        return self.clip >= 2 and self.ammo >= 2 and self.action in [self.StateReload,
                                                                     self.StateIdle,
                                                                     self.StateBeginReload,
                                                                     self.StateEndReload,
                                                                     self.StatePump]
            
    def canUse(self):
        return self.hasClip() and self.hasAmmo() and self.action in [self.StateReload,
                                                                     self.StateIdle,
                                                                     self.StateBeginReload,
                                                                     self.StateEndReload,
                                                                     self.StatePump]

    def secondaryFirePress(self, data):
        if not self.canUseSecondary():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateDblFire)

    def reloadPress(self, data):
        if self.action == self.StateIdle and not self.isClipFull() and self.ammo > self.clip:
            self.setNextAction(self.StateBeginReload)
        
    def unEquip(self):
        if not BaseHitscanAI.unEquip(self):
            return False
            
        if self.action == self.StateFire:
            self.needsPump = True
            
        return True

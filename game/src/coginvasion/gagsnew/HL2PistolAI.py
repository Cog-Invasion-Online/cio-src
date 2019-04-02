from BaseHitscanAI import BaseHitscanAI
from HL2PistolShared import HL2PistolShared
from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_HL2PISTOL

class HL2PistolAI(BaseHitscanAI, HL2PistolShared):

    Name = GagGlobals.HL2Pistol
    ID = ATTACK_HL2PISTOL
    HasClip = True
    UsesAmmo = True
    FriendlyFire = True

    FireDelay = 0.1
    AttackRange = 10000
    
    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   1.0,
                                   self.StateReload :   1.79,
                                   self.StateFire   :   0.5})
        self.maxAmmo = 150
        self.ammo = 150
        self.maxClip = 18
        self.clip = 18
                                   
    def determineNextAction(self, completedAction):
        if completedAction == self.StateIdle:
            if not self.hasClip():
                # Need to refill clip
                return self.StateReload
        elif completedAction == self.StateReload:
            # refill clip, but limit to ammo if ammo is less than clip size
            if self.ammo >= self.maxClip:
                self.clip = self.maxClip
            else:
                self.clip = self.ammo

        return self.StateIdle
            
    def canUse(self):
        return self.hasClip() and self.hasAmmo() and (self.action in [self.StateIdle, self.StateFire])

    def reloadPress(self, data):
        if self.action == self.StateIdle and not self.isClipFull() and self.ammo > self.clip:
            self.setNextAction(self.StateReload)

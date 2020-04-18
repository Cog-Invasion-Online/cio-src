from src.coginvasion.gagsnew.BaseGagAI import BaseGagAI
from src.coginvasion.attack.Attacks import ATTACK_SOUND
from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI

class SoundAI(BaseGagAI):

    ID = ATTACK_SOUND
    Name = "Sound"
    
    StateFire = 1
    
    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateFire: 5.0})
        self.didSound = False
        
    def equip(self):
        if not BaseGagAI.equip(self):
            return False
            
        self.b_setAction(self.StateIdle)

        return True
        
    def __doSound(self):
        self.didSound = True
        for av in self.avatar.air.avatars[self.avatar.getZoneId()]:
            if isinstance(av, DistributedSuitAI):
                if not av.isDead() and self.avatar.getDistance(av) <= 35.0:
                    av.npcStun()
                    
    def onSetAction(self, action):
        if action == self.StateFire:
            self.didSound = False
            
    def primaryFirePress(self, data = None):
        if not self.canUse():
            return
        self.b_setAction(self.StateFire)
        
    def think(self):
        BaseGagAI.think(self)
        
        if self.didSound:
            return
            
        if self.getAction() == self.StateFire:
            elapsed = self.getActionTime()
            if elapsed >= 3.0:
                self.__doSound()

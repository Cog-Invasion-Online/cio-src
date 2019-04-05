from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI
from src.coginvasion.cog.attacks import EvilEyeShared
from src.coginvasion.attack.Attacks import ATTACK_EVIL_EYE

class EvilEyeAI(GenericThrowAttackAI):
    #ID = ATTACK_EVIL_EYE
    
    def __init__(self):
        GenericThrowAttackAI.__init__(self, EvilEyeShared)
        
        self.ammo = 100
        self.maxAmmo = 100
        self.baseDamage = 21.0
            
    def calibrate(self, target):
        self.throwOrigin = self.avatar.getPos(render) + self.avatar.getEyePosition()
        self.traceOrigin = self.throwOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.throwOrigin).normalized()
    
    def checkCapable(self, _, squaredDistance):
        return squaredDistance <= 20*20 and squaredDistance > 8*8
    
    def getTauntChance(self):
        return 0.75
    
    def getTauntPhrases(self):
        return ["I'm giving you the evil eye.",
            "Could you eye-ball this for me?",
            "Wait. I've got something in my eye.",
            "I've got my eye on you!",
            "Could you keep an eye on this for me?",
            "I've got a real eye for evil.",
            "I'll poke you in the eye!",
            "\"Eye\" am as evil as they come!",
            "I'll put you in the eye of the storm!",
            "I'm rolling my eye at you."]

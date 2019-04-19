from src.coginvasion.cog.attacks import HardballShared
from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI

class HardballAI(GenericThrowAttackAI):

    def __init__(self):
        GenericThrowAttackAI.__init__(self, sharedMetadata = HardballShared.Metadata)
        self.ammo = 100
        self.maxAmmo = 100

    def getBaseDamage(self):
        return 25
        
    def getTauntChance(self):
        return 0.75
        
    def getTauntPhrases(self):
        return ['So you wanna play hardball?',
            "You don't wanna play hardball with me.",
            'Batter up!',
            'Hey batter, batter!',
            "And here's the pitch...",
            "You're going to need a relief pitcher.",
            "I'm going to knock you out of the park.",
            "Once you get hit, you'll run home.",
            'This is your final inning!',
            "You can't play with me!",
            "I'll strike you out.",
            "I'm throwing you a real curve ball!"]

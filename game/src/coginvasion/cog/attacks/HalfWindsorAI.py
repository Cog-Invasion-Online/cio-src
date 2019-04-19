from src.coginvasion.cog.attacks import HalfWindsorShared
from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI

class HalfWindsorAI(GenericThrowAttackAI):

    def __init__(self):
        GenericThrowAttackAI.__init__(self, sharedMetadata = HalfWindsorShared.Metadata)
        self.ammo = 100
        self.maxAmmo = 100

    def getBaseDamage(self):
        return 15
        
    def getTauntChance(self):
        return 0.75
        
    def getTauntPhrases(self):
        return ["This is the fanciest tie you'll ever see!",
            'Try not to get too winded.',
            "This isn't even half the trouble you're in.",
            "You're lucky I don't have a whole windsor.",
            "You can't afford this tie.",
            "I bet you've never even SEEN a half windsor!",
            'This tie is out of your league.',
            "I shouldn't even waste this tie on you.",
            "You're not even worth half of this tie!"]

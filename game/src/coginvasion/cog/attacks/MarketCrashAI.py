from src.coginvasion.cog.attacks import MarketCrashShared
from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI

class MarketCrashAI(GenericThrowAttackAI):

    def __init__(self):
        GenericThrowAttackAI.__init__(self, sharedMetadata = MarketCrashShared.Metadata)
        self.ammo = 100
        self.maxAmmo = 100

    def getBaseDamage(self):
        return 12
        
    def getTauntChance(self):
        return 0.5
        
    def getTauntPhrases(self):
        return ["I'm going to crash your party.",
            "You won't survive the crash.",
            "I'm more than the market can bear.",
            "I've got a real crash course for you!",
            "Now I'll come crashing down.",
            "I'm a real bull in the market.",
            'Looks like the market is going down.',
            'You had better get out quick!',
            'Sell! Sell! Sell!',
            'Shall I lead the recession?',
            "Everybody's getting out, shouldn't you?"]

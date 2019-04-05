from src.coginvasion.cog.attacks import SackedShared
from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI

class SackedAI(GenericThrowAttackAI):

    def __init__(self):
        GenericThrowAttackAI.__init__(self, sharedMetadata = SackedShared)
        self.ammo = 100
        self.maxAmmo = 100
        self.baseDamage = 16.0
        
    def getTauntChance(self):
        return 0.5
        
    def getTauntPhrases(self):
        return ["Looks like you're getting sacked.",
            "This one's in the bag.",
            "You've been bagged.",
            'Paper or plastic?',
            'My enemies shall be sacked!',
            'I hold the Toontown record in sacks per game.',
            "You're no longer wanted around here.",
            "Your time is up around here, you're being sacked!",
            'Let me bag that for you.',
            'No defense can match my sack attack!']

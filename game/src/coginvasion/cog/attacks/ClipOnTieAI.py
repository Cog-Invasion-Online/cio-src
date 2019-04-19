from src.coginvasion.cog.attacks import ClipOnTieShared
from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI

class ClipOnTieAI(GenericThrowAttackAI):

    def __init__(self):
        GenericThrowAttackAI.__init__(self, sharedMetadata = ClipOnTieShared.Metadata)
        self.ammo = 100
        self.maxAmmo = 100

    def getBaseDamage(self):
        return 20
        
    def getTauntChance(self):
        return 0.5
        
    def getTauntPhrases(self):
        return ['Better dress for our meeting.',
            "You can't go OUT without your tie.",
            'The best dressed Cogs wear them.',
            'Try this on for size.',
            'You should dress for success.',
            'No tie, no service.',
            'Do you need help putting this on?',
            'Nothing says powerful like a good tie.',
            "Let's see if this fits.",
            'This is going to choke you up.',
            "You'll want to dress up before you go OUT.",
            "I think I'll tie you up."]

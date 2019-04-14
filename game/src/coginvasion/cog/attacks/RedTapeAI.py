from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI
from src.coginvasion.cog.attacks import RedTapeShared

class RedTapeAI(GenericThrowAttackAI):
    
    def __init__(self):
        GenericThrowAttackAI.__init__(self, RedTapeShared)
        self.ammo = 100
        self.maxAmmo = 100

    def getBaseDamage(self):
        return 10
        
    def getTauntChance(self):
        return 0.5
    
    def getTauntPhrases(self):
        return ['This should wrap things up.',
             "I'm going to tie you up for awhile.",
             "You're on a roll.",
             'See if you can cut through this.',
             'This will get sticky.',
             "Hope you're claustrophobic.",
             "I'll make sure you stick around.",
             'Let me keep you busy.',
             'Just try to unravel this.',
             'I want this meeting to stick with you.']

from src.coginvasion.cog.attacks import BiteShared
from src.coginvasion.cog.attacks.GenericThrowAttackAI import GenericThrowAttackAI

class BiteAI(GenericThrowAttackAI):

    def __init__(self):
        GenericThrowAttackAI.__init__(self, sharedMetadata = BiteShared.Metadata)
        self.ammo = 100
        self.maxAmmo = 100

    def getBaseDamage(self):
        return 19.0
        
    def getTauntChance(self):
        return 0.75
        
    def getTauntPhrases(self):
        return ['Would you like a bite?',
          'Try a bite of this!',
          "You're biting off more than you can chew.",
          'My bite is bigger than my bark.',
          'Bite down on this!',
          'Watch out, I may bite.',
          "I don't just bite when I'm cornered.",
          "I'm just gonna grab a quick bite.",
          "I haven't had a bite all day.",
          'I just want a bite.  Is that too much to ask?']

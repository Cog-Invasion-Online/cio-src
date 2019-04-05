from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import BiteShared

class Bite(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, BiteShared)

from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import ClipOnTieShared

class ClipOnTie(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, ClipOnTieShared)

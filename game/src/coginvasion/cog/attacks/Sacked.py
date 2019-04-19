from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import SackedShared

class Sacked(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, SackedShared.Metadata)

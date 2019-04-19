from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import HardballShared

class Hardball(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, HardballShared.Metadata)

from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import HalfWindsorShared

class HalfWindsor(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, HalfWindsorShared.Metadata)

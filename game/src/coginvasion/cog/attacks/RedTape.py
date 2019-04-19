from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import RedTapeShared

class RedTape(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, RedTapeShared.Metadata)

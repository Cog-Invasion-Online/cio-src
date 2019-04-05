from src.coginvasion.cog.attacks.GenericThrowAttack import GenericThrowAttack
from src.coginvasion.cog.attacks import MarketCrashShared

class MarketCrash(GenericThrowAttack):
    
    def __init__(self):
        GenericThrowAttack.__init__(self, MarketCrashShared)

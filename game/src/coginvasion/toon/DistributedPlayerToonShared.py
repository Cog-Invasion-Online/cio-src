class DistributedPlayerToonShared:

    def __init__(self):
        self.sessionHealth = 100
        self.sessionMaxHealth = 100
        
    def useBackpack(self):
        bz = self.getBattleZone()
        return (not bz) or bz.getGameRules().useBackpack()
        
    def setSessionHealth(self, hp):
        self.sessionHealth = hp
        
    def getSessionHealth(self):
        return self.sessionHealth
        
    def setSessionMaxHealth(self, hp):
        self.sessionMaxHealth = hp
        
    def getSessionMaxHealth(self):
        return self.sessionMaxHealth
        
    def getHealth(self):
        if self.battleZone and not self.battleZone.getGameRules().useRealHealth():
            return self.sessionHealth
        
        return self.health
        
    def getMaxHealth(self):
        if self.battleZone and not self.battleZone.getGameRules().useRealHealth():
            return self.sessionMaxHealth
        
        return self.maxHealth
        
    def delete(self):
        del self.sessionHealth
        del self.sessionMaxHealth

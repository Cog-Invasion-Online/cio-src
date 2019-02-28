from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from DistributedEntityAI import DistributedEntityAI

from src.coginvasion.cog import Variant, SuitBank
#from src.coginvasion.cog.SuitBrainAI import SuitBrain
#from src.coginvasion.cog.SuitPursueToonBehaviorAI import SuitPursueToonBehaviorAI
from src.coginvasion.globals import CIGlobals

class DistributedSZBossSuitAI(DistributedSuitAI, DistributedEntityAI):
    
    GuardSuit = 4
    StartsActive = 8

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedSuitAI.__init__(self, air)
        self.setBattleZone(dispatch)
        dispatch.suits.append(self)
        
    def Activate(self):
        #self.stopPosHprBroadcast()
        #if self.brain:
        #    self.brain.startThinking()
        self.startAI()
            
    def Deactivate(self):
        #if self.brain:
        #    self.brain.stopThinking()
        self.stopAI()
            
    def Kill(self):
        self.b_setHealth(0)
        
    def delete(self):
        taskMgr.remove(self.uniqueName('monitorHealth'))
        DistributedEntityAI.delete(self)
        DistributedSuitAI.delete(self)
        self.battleZone = None
        
    def announceGenerate(self):
        entnum = self.cEntity.getEntnum()
        suitId = self.bspLoader.getEntityValueInt(entnum, "suitPlan")
        suitPlan = SuitBank.getSuitById(suitId)
        level = self.bspLoader.getEntityValueInt(entnum, "level")
        variant = self.bspLoader.getEntityValueInt(entnum, "variant")
        self.b_setLevel(level)
        self.b_setSuit(suitPlan, variant)
        self.b_setPlace(self.zoneId)
        self.b_setName(suitPlan.getName())
        
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        pos = self.getPos()
        hpr = self.getHpr()
        self.d_setPosHpr(pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
        
        DistributedEntityAI.announceGenerate(self)
        DistributedSuitAI.announceGenerate(self)
        self.stopAI()

        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))
        self.startPosHprBroadcast()
        
        spawnflags = self.bspLoader.getEntityValueInt(self.entnum, "spawnflags")
        if spawnflags & self.StartsActive:
            self.Activate()
        #elif spawnflags & self.GuardSuit:
            #self.b_setAnimState('neutral')

from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from DistributedEntityAI import DistributedEntityAI

from src.coginvasion.cog import Variant, SuitBank
from src.coginvasion.cog.SuitBrainAI import SuitBrain
from src.coginvasion.cog.SuitPursueToonBehaviorAI import SuitPursueToonBehaviorAI
from src.coginvasion.globals import CIGlobals

class DistributedSZBossSuitAI(DistributedSuitAI, DistributedEntityAI):

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedSuitAI.__init__(self, air)
        self.battleZone = dispatch
        self.battle = dispatch
        self.setManager(dispatch)
        dispatch.suits.append(self)
        
    def Activate(self):
        self.stopPosHprBroadcast()
        if self.brain:
            self.brain.startThinking()
            
    def Deactivate(self):
        if self.brain:
            self.brain.stopThinking()
            
    def Kill(self):
        self.b_setHealth(0)
        
    def spawn(self):
        self.brain = SuitBrain(self)
        pursue = SuitPursueToonBehaviorAI(self, self.getManager())
        pursue.battle = self.battle
        pursue.setSuitList(self.battleZone.suits)
        self.brain.addBehavior(pursue, priority = 1)
        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))
        self.startPosHprBroadcast()
        
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
        self.b_setLevel(level)
        self.b_setSuit(suitPlan, Variant.CORRODED)
        self.b_setPlace(self.zoneId)
        self.b_setName(suitPlan.getName())
        
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        pos = self.getPos()
        hpr = self.getHpr()
        self.d_setPosHpr(pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
        
        DistributedEntityAI.announceGenerate(self)
        DistributedSuitAI.announceGenerate(self)
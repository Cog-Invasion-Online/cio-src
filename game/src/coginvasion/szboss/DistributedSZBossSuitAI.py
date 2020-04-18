from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI

from src.coginvasion.attack.Attacks import AttackEnum
from src.coginvasion.cog import Variant, SuitBank
#from src.coginvasion.cog.SuitBrainAI import SuitBrain
#from src.coginvasion.cog.SuitPursueToonBehaviorAI import SuitPursueToonBehaviorAI
from src.coginvasion.globals import CIGlobals

class DistributedSZBossSuitAI(DistributedSuitAI):
    
    GuardSuit = 4
    StartsActive = 8

    def __init__(self, air, dispatch):
        DistributedSuitAI.__init__(self, air)
        self.setDispatch(dispatch)
        self.setBattleZone(dispatch)
        #dispatch.suits.append(self)
        
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
        DistributedSuitAI.delete(self)
        self.battleZone = None
        
    def monitorHealth(self, task):
        ret = DistributedSuitAI.monitorHealth(self, task)
        if self.isDead():
            self.dispatchOutput("OnDie")
            return task.done
        return ret
        
    def resetFwdSpeed(self):
        DistributedSuitAI.resetFwdSpeed(self)
        self.motor.fwdSpeed *= self.getEntityValueFloat("speedMod")
        
    def announceGenerate(self):
        entnum = self.cEntity.getBspEntnum()
        suitId = self.getEntityValueInt("suitPlan")
        suitPlan = SuitBank.getSuitById(suitId)
        level = self.getEntityValueInt("level")
        variant = self.getEntityValueInt("variant")
        self.b_setLevel(level)
        self.b_setSuit(suitPlan, variant)
        self.b_setPlace(self.zoneId)
        self.b_setName(suitPlan.getName())
        
        attackNames = self.getEntityValue("attacklist")
        if len(attackNames) > 0:
            attackNames = attackNames.split(';')
            attackIds = []
            for name in attackNames:
                attackIds.append(AttackEnum[name])
            self.b_setAttackIds(attackIds)
            
        #hp = self.getEntityValueInt("health")
        #if hp != -1:
        #    self.b_setMaxHealth(hp)
        #    self.b_setHealth(hp)
        
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        pos = self.getPos()
        hpr = self.getHpr()
        self.d_setPosHpr(pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
        
        DistributedSuitAI.announceGenerate(self)
        self.stopAI()

        #self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))
        self.startPosHprBroadcast()
        
        if self.spawnflags & self.StartsActive:
            self.Activate()
        #elif spawnflags & self.GuardSuit:
            #self.b_setAnimState('neutral')

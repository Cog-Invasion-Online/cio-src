from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon.DistributedToonAI import DistributedToonAI
from DistributedEntityAI import DistributedEntityAI
from src.coginvasion.npc import NPCGlobals
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI

class DistributedSZBossToonAI(DistributedEntityAI, DistributedToonAI, BaseNPCAI):
    notify = directNotify.newCategory("NPCToonAI")

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedToonAI.__init__(self, air)
        BaseNPCAI.__init__(self, dispatch)
        self.setBattleZone(dispatch)

        from src.coginvasion.avatar.Attacks import ATTACK_GAG_WHOLECREAMPIE
        self.attackIds = [ATTACK_GAG_WHOLECREAMPIE]

        self.died = False

    def delete(self):
        self.died = None
        taskMgr.remove(self.uniqueName('npcToonDie'))
        BaseNPCAI.delete(self)
        DistributedToonAI.delete(self)
        DistributedEntityAI.delete(self)

    def __die(self, task):
        self.requestDelete()
        return task.done

    def __hpChange(self, new, old):
        if new <= 0 and not self.died:
            # ded
            taskMgr.doMethodLater(7.0, self.__die, self.uniqueName('npcToonDie'))
            self.died = True

    def announceGenerate(self):
        npcName = self.getEntityValue("name")
        if len(npcName) == 0:
            npcId = self.getEntityValueInt("npcId")
        else:
            npcId = NPCGlobals.getNPCIDByName(npcName)

        name = NPCGlobals.NPCToonDict[npcId][1]
        dna = NPCGlobals.NPCToonDict[npcId][2]
        self.b_setName(name)
        self.b_setDNAStrand(dna)

        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())

        DistributedEntityAI.announceGenerate(self)
        DistributedToonAI.announceGenerate(self)

        self.b_setParent(CIGlobals.SPRender)
        self.startPosHprBroadcast()

        self.startAI()

        self.accept(self.getHealthChangeEvent(), self.__hpChange)

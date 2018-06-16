"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedToonInteriorAI.py
@author Brian Lach
@date July 27, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import DistributedObjectAI

from src.coginvasion.toon import DistributedNPCToonAI, DistributedHQNPCToonAI, DistributedTailorNPCToonAI, DistributedClerkNPCToonAI
from src.coginvasion.npc import NPCGlobals

import DistributedDoorAI

class DistributedToonInteriorAI(DistributedObjectAI.DistributedObjectAI):
    notify = directNotify.newCategory('DistributedToonInteriorAI')

    def __init__(self, air, block, doorToZone):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.door = None
        self.doorToZone = doorToZone
        self.block = block
        self.npcs = []

    def announceGenerate(self, doorType = 0):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        self.door = DistributedDoorAI.DistributedDoorAI(self.air, self.block, self.doorToZone, doorType)
        self.door.generateWithRequired(self.zoneId)
        self.createNPCs()

    def createNPCs(self):
        npcIdList = NPCGlobals.zone2NpcDict.get(self.zoneId, [])
        for npcId in npcIdList:
            while npcIdList.count(npcId) > 1:
                npcIdList.remove(npcId)
        for i in xrange(len(npcIdList)):
            npcId = npcIdList[i]
            npcData = NPCGlobals.NPCToonDict.get(npcId)
            if not npcData[3] in [NPCGlobals.NPC_REGULAR, NPCGlobals.NPC_HQ, NPCGlobals.NPC_TAILOR, NPCGlobals.NPC_CLERK]:
                continue
            if npcData[3] == NPCGlobals.NPC_REGULAR:
                npcClass = DistributedNPCToonAI.DistributedNPCToonAI
            elif npcData[3] == NPCGlobals.NPC_HQ:
                npcClass = DistributedHQNPCToonAI.DistributedHQNPCToonAI
            elif npcData[3] == NPCGlobals.NPC_TAILOR:
                npcClass = DistributedTailorNPCToonAI.DistributedTailorNPCToonAI
            elif npcData[3] == NPCGlobals.NPC_CLERK:
                npcClass = DistributedClerkNPCToonAI.DistributedClerkNPCToonAI
            npc = npcClass(self.air, npcId, len(self.npcs))
            npc.generateWithRequired(self.zoneId)
            self.npcs.append(npc)

    def delete(self):
        if self.door:
            self.door.requestDelete()
            self.door = None
        for npc in self.npcs:
            npc.requestDelete()
        self.npcs = None
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def setBlock(self, block):
        self.block = block

    def d_setBlock(self, block):
        self.sendUpdate('setBlock', [block])

    def b_setBlock(self, block):
        self.d_setBlock(block)
        self.setBlock(block)

    def getBlock(self):
        return self.block

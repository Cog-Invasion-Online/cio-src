########################################
# Filename: DeliverItemObjective.py
# Created by: DecodedLogic (19Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.quest.objective.VisitNPCObjective import VisitNPCObjective
from src.coginvasion.quest import QuestGlobals
from src.coginvasion.gags import GagGlobals

class DeliverItemObjective(VisitNPCObjective):
    notify = directNotify.newCategory('DeliverItemObjective')

    def __init__(self, npcId, itemName, itemAmount, assigner, location = None,
        itemIcon = QuestGlobals.getPackageIcon()):
        VisitNPCObjective.__init__(self, npcId, assigner, location, neededAmount = itemAmount)
        self.itemName = itemName
        self.itemIcon = itemIcon
        
        if self.itemName in GagGlobals.gagIds.values():
            self.itemIcon = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam').find('**/%s' % GagGlobals.InventoryIconByName[self.itemName])
    
    def getTaskInfo(self, speech=False):
        visitInfo = VisitNPCObjective.getTaskInfo(self, speech = False)
        infoText = '' if not speech else (QuestGlobals.DELIVER + ' ');
        infoText += str('a %s' % self.itemName) if self.neededAmount == 1 else str('%d %s' % (self.neededAmount, QuestGlobals.makePlural(self.itemName)))
        infoText = str('%s to %s' % (infoText, visitInfo))
        
        return infoText

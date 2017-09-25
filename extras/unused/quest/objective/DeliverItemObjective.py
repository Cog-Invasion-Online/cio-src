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

    def __init__(self, npcId, itemName, itemAmount, assignDialog, location = None,
        itemIcon = QuestGlobals.getPackageIcon()):
        VisitNPCObjective.__init__(self, npcId, assignDialog, location)
        self.itemName = itemName
        self.itemAmount = itemAmount
        self.itemIcon = itemIcon
        
        if self.itemName in GagGlobals.gagIds.values():
            self.itemIcon = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam').find('**/%s' % GagGlobals.InventoryIconByName[self.itemName])

    def updateInfo(self):
        VisitNPCObjective.updateInfo(self, False, QuestGlobals.DELIVER, QuestGlobals.RED)
        scale = 0.12 if self.itemIcon.getName() == 'package' else 0.85
        
        self.quest.setLeftIconGeom(self.itemIcon)
        self.quest.setLeftIconScale(scale)
        self.quest.setLeftPicturePos(QuestGlobals.RECOVER_LEFT_PICTURE_POS)
        if self.itemAmount > 1:
            self.quest.setInfoText('%d %s' % (self.itemAmount, QuestGlobals.makePlural(self.itemName)))
        else:
            self.quest.setInfoText(self.itemName)
        self.quest.setInfoPos(QuestGlobals.RECOVER_INFO_POS)
        self.quest.setMiddleText(QuestGlobals.TO)
        
    def getNeededAmount(self):
        return self.itemAmount

########################################
# Filename: DeliverItemObjective.py
# Created by: DecodedLogic (19Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.quest.VisitNPCObjective import VisitNPCObjective
from lib.coginvasion.quest import QuestGlobals

class DeliverItemObjective(VisitNPCObjective):
    notify = directNotify.newCategory('DeliverItemObjective')
    
    def __init__(self, npcId, itemName, quest, assignDialog, location = None, 
        itemIcon = QuestGlobals.getPackageIcon()):
        VisitNPCObjective.__init__(self, npcId, quest, assignDialog, location)
        self.itemName = itemName
        self.itemIcon = itemIcon
        
    def updateInfo(self):
        VisitNPCObjective.updateInfo(self, False, QuestGlobals.DELIVER, QuestGlobals.RED)
        self.quest.setLeftIconGeom(self.itemIcon)
        self.quest.setLeftIconScale(self.itemIcon.getScale())
        self.quest.setLeftPicturePos(QuestGlobals.RECOVER_LEFT_PICTURE_POS)
        self.quest.setInfoText(self.itemName)
        self.quest.setInfoPos(QuestGlobals.RECOVER_INFO_POS)
        self.quest.setMiddleText(QuestGlobals.TO)
        
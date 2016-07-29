########################################
# Filename: RecoverItemObjective.py
# Created by: DecodedLogic (19Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.quest.CogObjective import CogObjective
from lib.coginvasion.quest import QuestGlobals

class RecoverItemObjective(CogObjective):
    notify = directNotify.newCategory('RecoverItemObjective')

    def __init__(self, amount, itemName, assignDialog, location = None,
        itemIcon = QuestGlobals.getPackageIcon(), level = None, levelRange = None, name = None,
        variant = None, dept = None):
        CogObjective.__init__(self, location, assignDialog, amount, level = level, levelRange = levelRange,
            name = name, variant = variant, dept = dept)
        self.itemName = itemName
        self.itemIcon = itemIcon

    def updateInfo(self):
        CogObjective.updateInfo(self, False, QuestGlobals.RECOVER, QuestGlobals.GREEN)
        self.quest.setLeftIconGeom(self.itemIcon)
        self.quest.setLeftIconScale(self.itemIcon.getScale())
        self.quest.setLeftPicturePos(QuestGlobals.RECOVER_LEFT_PICTURE_POS)
        self.quest.setInfoText(self.itemName)
        self.quest.setInfoPos(QuestGlobals.RECOVER_INFO_POS)
        self.quest.setMiddleText(QuestGlobals.FROM)

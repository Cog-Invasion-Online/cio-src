########################################
# Filename: VisitNPCObjective.py
# Created by: DecodedLogic (18Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quest.Objective import Objective
from lib.coginvasion.quest import QuestGlobals
from lib.coginvasion.toon.ToonDNA import ToonDNA
from lib.coginvasion.toon.ToonHead import ToonHead

class VisitNPCObjective(Objective):
    notify = directNotify.newCategory('VisitNPCObjective')

    def __init__(self, npcId, assignDialog, location = None):
        location = CIGlobals.NPCToonDict.get(npcId)[0] if not location else location
        Objective.__init__(self, location, assignDialog)
        self.npcId = npcId
        self.didEditLeft = True

    def updateInfo(self, useLeftFrame = True, auxText = QuestGlobals.VISIT,
            frameColor = QuestGlobals.BROWN):
        Objective.updateInfo(self)
        self.didEditLeft = useLeftFrame

        # Let's generate the head.
        dna = ToonDNA()
        dna.setDNAStrand(CIGlobals.NPCToonDict.get(self.npcId)[2])
        head = ToonHead(base.cr)
        head.generateHead(dna.getGender(), dna.getAnimal(), dna.getHead(), forGui = 1)
        head.setHeadColor(dna.getHeadColor())

        # Update whichever frame and the text below it that was chosen.
        if useLeftFrame:
            self.quest.setLeftIconGeom(head)
            self.quest.setInfoText(CIGlobals.NPCToonNames[self.npcId])
        else:
            self.quest.setRightIconGeom(head)
            self.quest.setRightPicturePos(QuestGlobals.DEFAULT_RIGHT_PICTURE_POS)
            self.quest.setInfo02Text(CIGlobals.NPCToonNames[self.npcId])
            self.quest.setInfo02Pos(QuestGlobals.RECOVER_INFO2_POS)
            self.quest.setAuxPos(QuestGlobals.RECOVER_AUX_POS)

        self.quest.setAuxText(auxText)
        self.quest.setPictureFrameColor(frameColor)

    def getNPCId(self):
        return self.npcId

    def getDidEditLeft(self):
        return self.didEditLeft

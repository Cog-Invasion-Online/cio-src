"""

  Filename: AvChooser.py
  Created by: blach (10Nov14)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.fsm.StateData import StateData
from lib.coginvasion.globals import CIGlobals, ChatGlobals
from lib.coginvasion.holiday.HolidayManager import HolidayType, HolidayGlobals
from lib.coginvasion.gui.WhisperPopup import WhisperPopup
from AvChoice import AvChoice
from CharSelection import CharSelection

class AvChooser(StateData):
    notify = directNotify.newCategory("AvChooser")

    def __init__(self, parentFSM):
        StateData.__init__(self, "avChooseDone")
        self.avChooseFSM = ClassicFSM('avChoose', [State('getToonData', self.enterGetToonData, self.exitGetToonData),
                                State('avChoose', self.enterAvChoose, self.exitAvChoose),
                                State('waitForToonDelResponse', self.enterWaitForToonDelResponse,
                                    self.exitWaitForToonDelResponse),
                                State('off', self.enterOff, self.exitOff)], 'off', 'off')
        self.avChooseFSM.enterInitialState()
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('avChoose').addChild(self.avChooseFSM)
        self.pickAToon = None
        self.setAvatarsNone()

    def enter(self):
        StateData.enter(self)
        base.transitions.noTransitions()
        self.avChooseFSM.request('getToonData')

    def exit(self):
        StateData.exit(self)
        self.setAvatarsNone()
        self.avChooseFSM.requestFinalState()

    def setAvatarsNone(self):
        self.avChoices = []

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterGetToonData(self):
        # Get the data for the avatars tied into this account.
        self.acceptOnce(base.cr.csm.getSetAvatarsEvent(), self.handleToonData)
        base.cr.csm.d_requestAvatars()

    def handleToonData(self, avatarList):
        for av in avatarList:
            avId = av[0]
            dna = av[1]
            name = av[2]
            slot = av[3]
            choice = AvChoice(dna, name, slot, avId)
            self.avChoices.append(choice)
        self.avChooseFSM.request('avChoose')

    def exitGetToonData(self):
        self.ignore(base.cr.csm.getSetAvatarsEvent())

    def enterAvChoose(self):
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            base.cr.music.stop()
            base.cr.music = base.loadMusic(CIGlobals.getHolidayTheme())
            base.cr.music.setLoop(True)
            base.cr.music.setVolume(0.75)
            base.cr.music.play()

            # Create message.
            whisper = WhisperPopup(HolidayGlobals.CHRISTMAS_TIME, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
            whisper.manage(base.marginManager)

        self.pickAToon = CharSelection(self)
        self.pickAToon.load()

    def enterWaitForToonDelResponse(self, avId):
        self.acceptOnce(base.cr.csm.getToonDeletedEvent(), self.handleDeleteToonResp)
        base.cr.csm.sendDeleteToon(avId)

    def exitWaitForToonDelResponse(self):
        self.ignore(base.cr.csm.getToonDeletedEvent())

    def hasToonInSlot(self, slot):
        if self.getAvChoiceBySlot(slot) != None:
            return True
        else:
            return False

    def getNameInSlot(self, slot):
        return self.getAvChoiceBySlot(slot).getName()

    def getNameFromAvId(self, avId):
        for avChoice in self.avChoices:
            if avChoice.getAvId() == avId:
                return avChoice.getName()

    def getAvChoiceBySlot(self, slot):
        for avChoice in self.avChoices:
            if avChoice.getSlot() == slot:
                return avChoice
        return None

    def getHeadInfo(self, slot):
        dna = self.getAvChoiceBySlot(slot).getDNA()
        self.pickAToon.dna.setDNAStrand(dna)
        return [self.pickAToon.dna.getGender(), self.pickAToon.dna.getAnimal(),
            self.pickAToon.dna.getHead(), self.pickAToon.dna.getHeadColor()]

    def handleDeleteToonResp(self):
        base.cr.loginFSM.request('avChoose')

    def exitAvChoose(self):
        self.pickAToon.unload()
        self.pickAToon = None

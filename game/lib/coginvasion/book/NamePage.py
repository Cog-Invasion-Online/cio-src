########################################
# Filename: NamePage.py
# Created by: DecodedLogic (12Apr16)
########################################

from direct.fsm.StateData import StateData
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from lib.coginvasion.globals import CIGlobals
from direct.gui.DirectGui import DirectScrolledList, DGG, DirectButton, OnscreenText
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import TextNode

listXorigin = -0.02
listFrameSizeX = 0.625
listZorigin = -0.96
listFrameSizeZ = 1.04
arrowButtonScale = 1.3
itemFrameXorigin = -0.237
itemFrameZorigin = 0.365
buttonXstart = itemFrameXorigin + 0.293

class NameData:

    def __init__(self, name, date, avId, accountId):
        self.name = name
        self.date = date
        self.avId = avId
        self.accId = accountId

class NamePage(StateData):
    notify = directNotify.newCategory('NamePage')

    def __init__(self, book, parentFSM):
        self.book = book
        self.parentFSM = parentFSM
        StateData.__init__(self, 'namePageDone')
        self.fsm = ClassicFSM('NamePage', [State('off', self.enterOff, self.exitOff),
            State('basePage', self.enterBasePage, self.exitBasePage)],
        'off', 'off')
        self.fsm.enterInitialState()
        self.parentFSM.getStateNamed('namePage').addChild(self.fsm)
        self.nameServ = base.cr.nameServicesManager
        self.baseRequestIndex = 0
        self.requestsPerCluster = 5

        # GUI elements
        self.requestsContainer = {}
        self.loadingLabel = None
        self.selectedName = None
        self.nameButtons = []
        self.avId2NameData = {}

        geom = CIGlobals.getDefaultBtnGeom()
        self.acceptBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 0.5,
            text = "Accept",
            pos = (0.5, posY, 0),
            text_pos = (0, -0.01),
            command = self.acceptName,
        )
        self.acceptBtn.hide()
        self.declineBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 0.5,
            text = "Decline",
            pos = (0.75, posY, 0),
            text_pos = (0, -0.01),
            command = self.declineName,
        )
        self.declineBtn.hide()
        self.avIdLbl = OnscreenText(text = "", scale = 0.08, pos = (0.3, 0, 0.5), align = TextNode.ACenter)
        self.avIdLbl.hide()
        self.accIdLbl = OnscreenText(text = "", scale = 0.08, pos = (0.3, 0, 0.3), align = TextNode.ACenter)
        self.accIdLbl.hide()

    def handleRequests(self):
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        self.nameList = DirectScrolledList(
            relief=None,
            pos=(-0.54, 0, 0.08),
            incButton_image=(gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')),
            incButton_relief=None,
            incButton_scale=(arrowButtonScale, arrowButtonScale, -arrowButtonScale),
            incButton_pos=(buttonXstart, 0, itemFrameZorigin - 0.999),
            incButton_image3_color=Vec4(1, 1, 1, 0.2),
            incButton_command = self.__moveItems,
            incButton_extraArgs = [1],
            decButton_image=(gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')),
            decButton_relief=None,
            decButton_scale=(arrowButtonScale, arrowButtonScale, arrowButtonScale),
            decButton_pos=(buttonXstart, 0, itemFrameZorigin + 0.125),
            decButton_image3_color=Vec4(1, 1, 1, 0.2),
            decButton_command = self.__moveItems,
            decButton_extraArgs = [0],
            itemFrame_pos=(itemFrameXorigin, 0, itemFrameZorigin),
            itemFrame_scale=1.0,
            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(listXorigin,
                listXorigin + listFrameSizeX,
                listZorigin,
                listZorigin + listFrameSizeZ),
            itemFrame_frameColor=(0.85, 0.95, 1, 1),
            itemFrame_borderWidth=(0.01, 0.01),
            numItemsVisible=5,
            forceHeight=0.075,
            items=self.nameButtons
        )
        self.__buildItems()

    def __moveItems(self, direction):
        if direction == 0:
            # Moving down!
            self.baseRequestIndex += 1
        elif direction == 1:
            # Moving up!
            self.baseRequestIndex -= 1
        self.clearItems()
        self.__buildItems()

    def clearItems(self):
        for btn in self.nameButtons:
            btn.destroy()
        self.nameButtons = []
        self.nameList.removeAndDestroyAllItems()

    def __buildItems(self):
        for i in xrange(self.requestsPerCluster):
            request = self.nameServ.getNameRequests()[self.baseRequestIndex + i]
            date = request['date']
            date = date.replace(' ', '-')

            data = NameData(request['name'], date, request['avId'], request['accId'])
            self.avId2NameData[data.avId] = data

            btn = DirectButton(
                relief=None, text=data.name, text_scale=0.07,
                text_align=TextNode.ALeft, text1_bg=textDownColor, text2_bg=textRolloverColor,
                text3_fg=textDisabledColor, textMayChange=0, command=self.__handleNameButton,
                extraArgs=[data], text_pos = (0, 0, 0.0)
            )

            data.btn = btn

            self.nameButtons.append(btn)
        self.loadingLabel.hide()

    def __handleNameButton(self, data):
        self.selectedName = data
        data.btn['state'] = DGG.DISABLED
        self.avIdLbl.setText("Avatar ID:\n" + str(data.avId))
        self.avIdLbl.show()
        self.accIdLbl.setText("Account ID:\n" + str(data.accId))
        self.accIdLbl.show()
        self.acceptBtn.show()
        self.declineBtn.show()

    def acceptName(self):
        pass

    def load(self):
        StateData.load(self)
        self.loadingLabel = OnscreenText(text = 'Loading...',
            font = CIGlobals.getToonFont(), pos = (0, 0.1, 0), scale = 0.08, parent = aspect2d)

    def unload(self):
        StateData.unload(self)
        self.loadingLabel.destroy()
        self.loadingLabel = None
        for request in self.requestsContainer.values():
            for element in request:
                element.destroy()
        self.requestsContainer = {}

    def enter(self):
        StateData.enter(self)
        self.fsm.request('basePage')
        base.acceptOnce(self.nameServ.getRequestCompleteName(), self.handleRequests)
        self.nameServ.d_requestNameData()

    def exit(self):
        self.fsm.requestFinalState()
        StateData.exit(self)

    def enterBasePage(self):
        self.book.createPageButtons('adminPage', None)
        self.book.setTitle('Name Approval')

    def exitBasePage(self):
        self.book.deletePageButtons(True, False)
        self.book.clearTitle()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

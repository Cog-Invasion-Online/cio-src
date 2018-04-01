"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdminTokenDialog.py
@author Brian Lach
@date September 05, 2016

@desc For the UI that shows when we are changing someone's admin token.

"""

from panda3d.core import TextNode, Vec4

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectButton, DGG, DirectScrolledList

from src.coginvasion.gui import Dialog
from src.coginvasion.globals import CIGlobals
from src.coginvasion.distributed import AdminCommands

class AdminTokenDialog(Dialog.GlobalDialog):
    notify = directNotify.newCategory("AdminTokenDialog")
    
    def __init__(self):
        Dialog.GlobalDialog.__init__(self, "Click on the Toon who you want to modify the Admin Token of...",
                                     "adminTokenCancel", Dialog.Cancel, CIGlobals.DialogOk, CIGlobals.DialogCancel,
                                     [], text_align = TextNode.ACenter, pos = (0, 0, 0.8), scale = 0.7)
        self.acceptOnce("adminTokenCancel", self.__handleCancel)
        self.acceptOnce(base.cr.playGame.getPlace().doneEvent, self.__handleCancel)
        base.localAvatar.clickToonCallback = self.__handleClickToon
        self.tokBtns = []
        self.tokList = None
        self.choiceDialog = None
        self.initialiseoptions(AdminTokenDialog)
        
    def __handleCancel(self):
        self.ignore(base.cr.playGame.getPlace().doneEvent)
        self.ignore("adminTokenCancel")
        self.ignore("invalidToonAck")
        self.ignore("tsaChoice")
        base.localAvatar.clickToonCallback = None
        if self.tokBtns is not None:
            for btn in self.tokBtns:
                btn.destroy()
            self.tokBtns = None
        if self.tokList:
            self.tokList.destroy()
            self.tokList = None
        if self.choiceDialog:
            self.choiceDialog.cleanup()
            self.choiceDialog = None
        try:
            self.cleanup()
        except:
            pass
        
    def __handleInvalidToonAck(self):
        if self.choiceDialog:
            self.choiceDialog.cleanup()
            self.choiceDialog = None
        base.localAvatar.clickToonCallback = self.__handleClickToon
        
    def __handleClickToon(self, avId):
        toon = base.cr.doId2do.get(avId)
        
        if not toon:
            return
        
        if toon.getAdminToken() == AdminCommands.DevToken:
            self.choiceDialog = Dialog.GlobalDialog("You cannot set the Admin Token of a {0}.".format(
                                                    AdminCommands.TextByAdminToken[AdminCommands.DevToken]), "invalidToonAck",
                                                    Dialog.Ok)
            self.choiceDialog.show()
            self.acceptOnce("invalidToonAck", self.__handleInvalidToonAck)
            return
        
        self.choiceDialog = Dialog.GlobalDialog("Set the Admin Token of {0}:".format(toon.getName()), "", Dialog.NoButtons,
                             CIGlobals.DialogOk, CIGlobals.DialogCancel,
                             [], text_align = TextNode.ACenter)
        #self.choiceDialog['text_align']  = TextNode.ACenter
        self.choiceDialog['image_scale'] = (1.2, 0, 1)
        self.choiceDialog['image_pos']   = (0,   0, -0.4)
        self.choiceDialog.setPos(0, 0.35, 0.35)
        self.choiceDialog.show()

        textRolloverColor = Vec4(1, 1, 0, 1)
        textDownColor = Vec4(0.5, 0.9, 1, 1)
        textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)


        self.tokBtns = []

        for tId, tName in AdminCommands.TextByAdminToken.items():
            btn = DirectButton(
                        relief=None, text = tName, text_scale=0.06,
                        text_align=TextNode.ALeft, text1_bg=textDownColor, text2_bg=textRolloverColor,
                        text3_fg=textDisabledColor, textMayChange=0, command=self.__handleClickToken,
                        extraArgs=[avId, tId], text_pos = (0, 0, 0.0)
            )
            self.tokBtns.append(btn)

        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        listXorigin = -0.02
        listFrameSizeX = 0.625
        listZorigin = -0.43
        listFrameSizeZ = 0.51
        arrowButtonScale = 0.0
        itemFrameXorigin = -0.237
        itemFrameZorigin = 0.365
        buttonXstart = itemFrameXorigin + 0.293

        self.tokList = DirectScrolledList(
                    relief=None,
                    pos=(-0.065, 0, -0.65),
                    incButton_image=None,
                    incButton_scale=(arrowButtonScale, arrowButtonScale, -arrowButtonScale),
                    decButton_image=None,
                    decButton_scale=(arrowButtonScale, arrowButtonScale, arrowButtonScale),
                    itemFrame_pos=(itemFrameXorigin, 0, itemFrameZorigin),
                    itemFrame_scale=1.0,
                    itemFrame_relief=DGG.SUNKEN,
                    itemFrame_frameSize=(listXorigin,
                        listXorigin + listFrameSizeX,
                        listZorigin,
                        listZorigin + listFrameSizeZ),
                    itemFrame_frameColor=(0.85, 0.95, 1, 1),
                    itemFrame_borderWidth=(0.01, 0.01),
                    numItemsVisible=15,
                    forceHeight=0.075,
                    items=self.tokBtns,
                    parent = self.choiceDialog
        )
        
    def __handleClickToken(self, avId, token):
        REQ_SET_ADMIN_TOKEN(avId, token)
        pref = "Give"
        if token == AdminCommands.NoToken:
            pref = "Remove"
        self.choiceDialog.cleanup()
        self.choiceDialog = Dialog.GlobalDialog(pref + " TSA uniform?", "tsaChoice", Dialog.YesNo)
        self.choiceDialog.show()
        self.acceptOnce("tsaChoice", self.__handleTSAChoice, [avId, token])
        
    def __handleTSAChoice(self, avId, token):
        toon = base.cr.doId2do.get(avId)
        val = self.choiceDialog.getValue()
        if token > AdminCommands.NoToken:
            if val:
                REQ_SET_TSA_UNI(avId, 1)
        elif token == AdminCommands.NoToken:
            if val and toon.hasTSASuit():
                REQ_SET_TSA_UNI(avId, 0)
        self.__handleCancel()

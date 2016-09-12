# COG INVASION ONLINE
# Copyright (c) Brian Lach       <brianlach72@gmail.com>
#               Maverick Liberty <maverick.liberty29@gmail.com>
#
# file:    WorldAccessDialog.py
# author:  Brian Lach
# date:    2016-09-12
#
# purpose: Admin dialog for giving world and tp access to players.

from panda3d.core import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
import Dialog

class WorldAccessDialog(Dialog.GlobalDialog):
    notify = directNotify.newCategory("WorldAccessDialog")
    
    def __init__(self):
        Dialog.GlobalDialog.__init__(self, "Click on the Toon who you want to give world access to...",
                                     "worldAccessCancel", Dialog.Cancel, CIGlobals.DialogOk, CIGlobals.DialogCancel,
                                     [], text_align = TextNode.ACenter, pos = (0, 0, 0.8), scale = 0.7)
        self.acceptOnce("worldAccessCancel", self.__handleCancel)
        self.acceptOnce(base.cr.playGame.getPlace().doneEvent, self.__handleCancel)
        base.localAvatar.clickToonCallback = self.__handleClickToon
        self.choiceDialog = None
        self.initialiseoptions(WorldAccessDialog)
        
    def __handleCancel(self):
        self.ignore(base.cr.playGame.getPlace().doneEvent)
        self.ignore("worldAccessCancel")
        self.ignore("tpAccessChoice")
        base.localAvatar.clickToonCallback = None
        if self.choiceDialog:
            self.choiceDialog.cleanup()
            self.choiceDialog = None
        try:
            self.cleanup()
        except:
            pass
            
    def __handleClickToon(self, avId):
        self.choiceDialog = Dialog.GlobalDialog("And give teleport access?", "tpAccessChoice", Dialog.YesNo)
        self.acceptOnce("tpAccessChoice", self.__handleTPAccessChoice, [avId])
        self.choiceDialog.show()
        
    def __handleTPAccessChoice(self, avId):
        value = self.choiceDialog.getValue()
        if value:
            REQ_SET_WORLD_ACCESS(avId, 1)
        else:
            REQ_SET_WORLD_ACCESS(avId, 0)
        self.__handleCancel()
        
# COG INVASION ONLINE
# Copyright (c) Brian Lach       <brianlach72@gmail.com>
#               Maverick Liberty <maverick.liberty29@gmail.com>
#
# file:    KickBanDialog.py
# author:  Brian Lach
# date:    2016-09-05
#
# purpose: This is the dialog window that appears when we are
#          prompted to click on a Toon to kick or ban.

from pandac.PandaModules import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.gui import Dialog
from lib.coginvasion.globals import CIGlobals

class KickBanDialog(Dialog.GlobalDialog):
    notify = directNotify.newCategory("KickBanDialog")
    
    def __init__(self, ban = 0):
        msg = "Click on the Toon you want to kick"
        if ban:
            msg += " and ban..."
        else:
            msg += "..."
        self.ban = ban
        Dialog.GlobalDialog.__init__(self, msg, "kickBanCancel", Dialog.Cancel, CIGlobals.DialogOk,
            CIGlobals.DialogCancel, [], text_align = TextNode.ACenter, pos = (0, 0, 0.8), scale = 0.7)
        self.acceptOnce("kickBanCancel", self.__handleCancel)
        self.acceptOnce(base.cr.playGame.getPlace().doneEvent, self.__handleCancel)
        base.localAvatar.clickToonCallback = self.__handleClickToon
        self.initialiseoptions(KickBanDialog)
        
    def __handleClickToon(self, avId):
        SEND_KICK_MSG(avId, self.ban)
        self.__handleCancel()
        
    def __handleCancel(self):
        self.ignore(base.cr.playGame.getPlace().doneEvent)
        self.ignore("kickBanCancel")
        self.cleanup()
        base.localAvatar.clickToonCallback = None
        del self.ban
        
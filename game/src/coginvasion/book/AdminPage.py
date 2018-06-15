"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AdminPage.py
@author Maverick Liberty
@date June 18, 2016

"""

from panda3d.core import SceneGraphAnalyzer, LineStream, PStatClient
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.gui.DirectGui import OnscreenText, DirectButton, DirectEntry

from src.coginvasion.globals import CIGlobals
from src.coginvasion.book.BookPage import BookPage

from src.coginvasion.gui.KickBanDialog import KickBanDialog
from src.coginvasion.gui.AdminTokenDialog import AdminTokenDialog
from src.coginvasion.gui.WorldAccessDialog import WorldAccessDialog
from src.coginvasion.gui.Dialog import GlobalDialog, Ok

class AdminPage(BookPage):

    def __init__(self, book):
        BookPage.__init__(self, book, 'Admin Panel')
        self.fsm = ClassicFSM('AdminPage', [State('off', self.enterOff, self.exitOff),
            State('basePage', self.enterBasePage, self.exitBasePage),
            State('kickSection', self.enterKickSection, self.exitKickSection),
            #State('clickOnToon', self.enterClickOnToon, self.exitClickOnToon),
            State('sysMsgSection', self.enterSysMsgSection, self.exitSysMsgSection)],
            'off', 'off')
        self.fsm.enterInitialState()

    def load(self):
        BookPage.load(self)
        icons = loader.loadModel('phase_4/models/gui/tfa_images.bam')
        self.icon = icons.find('**/hq-dialog-image')
        icons.detachNode()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enter(self):
        BookPage.enter(self)
        self.fsm.request('basePage')

    def exit(self):
        self.fsm.requestFinalState()
        BookPage.exit(self)

    def unload(self):
        del self.book
        del self.fsm
        BookPage.unload(self)

    def enterSysMsgSection(self):
        geom = CIGlobals.getDefaultBtnGeom()
        self.infoLbl = OnscreenText(text = "Inform all online players about something.", pos = (0, 0.45))
        self.msgEntry = DirectEntry(
            initialText = "System Message...",
            scale = 0.055,
            width = 15,
            numLines = 4,
            command = self.sendSystemMessageCommand,
            focusInCommand = base.localAvatar.chatInput.disableKeyboardShortcuts,
            focusOutCommand = base.localAvatar.chatInput.enableKeyboardShortcuts,
            pos = (-0.4, 0, 0)

        )
        self.sendBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Send",
            pos = (0, 0, -0.35),
            text_pos = (0, -0.01),
            command = self.sendSystemMessageCommand,
        )
        self.cancelBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Cancel",
            pos = (-0.45, 0.15, -0.55),
            text_pos = (0, -0.01),
            command = self.fsm.request,
            extraArgs = ['basePage']
        )
    
    # Occasionally, extra arguments are sent and this extra variable must be here to capture them.
    def sendSystemMessageCommand(self, _ = None):
        msg = self.msgEntry.get()
        DISTRICT_WIDE_MSG(msg)
        self.fsm.request('basePage')

    def exitSysMsgSection(self):
        self.infoLbl.destroy()
        del self.infoLbl
        self.msgEntry.destroy()
        del self.msgEntry
        self.sendBtn.destroy()
        del self.sendBtn
        self.cancelBtn.destroy()
        del self.cancelBtn

    def enterKickSection(self):
        geom = CIGlobals.getDefaultBtnGeom()
        self.infoLbl = OnscreenText(text = "Kick or Ban?", pos = (0, 0.45))
        self.kickBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Kick",
            pos = (0, 0, 0.1),
            text_pos = (0, -0.01),
            command = self.book.finishedResume,
            extraArgs = [KickBanDialog, [0]]
        )
        self.banBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Ban",
            pos = (0, 0, 0.0),
            text_pos = (0, -0.01),
            command = self.book.finishedResume,
            extraArgs = [KickBanDialog, [1]]
        )
        self.cancelBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Cancel",
            pos = (-0.45, 0.15, -0.45),
            text_pos = (0, -0.01),
            command = self.fsm.request,
            extraArgs = ['basePage']
        )

    def exitKickSection(self):
        self.banBtn.destroy()
        del self.banBtn
        self.infoLbl.destroy()
        del self.infoLbl
        self.cancelBtn.destroy()
        del self.cancelBtn
        self.kickBtn.destroy()
        del self.kickBtn

    def enterBasePage(self):
        geom = CIGlobals.getDefaultBtnGeom()
        self.ghostBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Toggle Ghost",
            pos = (-0.45, 0.15, 0.5),
            text_pos = (0, -0.01),
            command = TOGGLE_GHOST
        )
        self.bgBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Toggle Background",
            pos = (-0.45, 0.15, 0.40),
            text_pos = (0, -0.01),
            command = self.toggleBackground
        )
        self.idBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Toggle Player Ids",
            pos = (-0.45, 0.15, 0.3),
            text_pos = (0, -0.01),
            command = TOGGLE_PLAYER_IDS
        )
        self.kickBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Kick/Ban Player",
            pos = (0.45, 0.15, 0.5),
            text_pos = (0, -0.01),
            command = self.openKickPage
        )
        self.systemMsgBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "System Message",
            pos = (-0.45, 0.15, 0.1),
            text_pos = (0, -0.01),
            command = self.openSysMsgPage
        )
        self.oobeBtn = DirectButton(
            geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Toggle OOBE",
			pos = (-0.45, 0.15, 0.2),
			text_pos = (0, -0.01),
			command = base.oobe
        )
        self.directBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Start DIRECT",
            pos = (-0.45, 0.15, 0.1),
            text_pos = (0, -0.01),
            command = self.doStartDirect
        )
        self.pstatsBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Toggle PStats",
            pos = (-0.45, 0.15, 0.0),
            text_pos = (0, -0.01),
            command = self.togglePStats
        )
        self.tokenBtn = DirectButton(
            geom = geom,
			text_scale = 0.04,
			relief = None,
			scale = 1.0,
			text = "Modify Admin Token",
			pos = (0.45, 0.15, 0.4),
			text_pos = (0, -0.01),
			command = self.book.finishedResume,
            extraArgs = [AdminTokenDialog, []]
        )
        self.worldBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Give World Access",
            pos = (0.45, 0.15, 0.3),
            text_pos = (0, -0.01),
            command = self.book.finishedResume,
            extraArgs = [WorldAccessDialog, []]
        )
        self.allGagsBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Unlock All Gags",
            pos = (0.45, 0.15, 0.2),
            text_pos = (0, -0.01),
            command = SEND_REQ_UNLOCK_GAGS
        )
        self.allSlotsBtn = DirectButton(
            geom = geom,
            text_scale = 0.0375,
            relief = None,
            scale = 1.0,
            text = "Unlock All Gag Slots",
            pos = (0.45, 0.15, 0.1),
            text_pos = (0, -0.01),
            command = SEND_REQ_GAG_SLOTS
        )
        self.physDbgBtn = DirectButton(
            geom = geom,
            text_scale = 0.039,
            relief = None,
            scale = 1.0,
            text = "Toggle Physics Debug",
            pos = (0.45, 0.15, 0.0),
            text_pos = (0, -0.01),
            command = self.togglePhysDbg
        )
        self.analyzeBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "Analyze Scene",
            pos = (0.45, 0.15, -0.1),
            text_pos = (0, -0.01),
            command = self.doAnalyzeScene
        )
        self.listBtn = DirectButton(
            geom = geom,
            text_scale = 0.04,
            relief = None,
            scale = 1.0,
            text = "List Scene",
            pos = (0.45, 0.15, -0.2),
            text_pos = (0, -0.01),
            command = render.ls
        )
        base.cr.playGame.getPlace().maybeUpdateAdminPage()
        del geom

    def doStartDirect(self):
        base.startTk()
        base.startDirect()

    def doAnalyzeScene(self):
        ls = LineStream()
        sga = SceneGraphAnalyzer()
        sga.addNode(render.node())
        sga.write(ls)
        text = ""
        while ls.isTextAvailable():
            text += ls.getLine() + "\n"
        self.acceptOnce('analyzedone', self.__handleAnalyzeDone)
        self.analyzeDlg = GlobalDialog(message = text, style = Ok,
                                       doneEvent = 'analyzedone',
                                       text_scale = 0.05)
        self.analyzeDlg.show()

    def __handleAnalyzeDone(self):
        self.analyzeDlg.cleanup()
        del self.analyzeDlg

    def togglePhysDbg(self):
        base.setPhysicsDebug(not base.physicsDbgFlag)

    def togglePStats(self):
        if PStatClient.isConnected():
            PStatClient.disconnect()
        else:
            PStatClient.connect()

    def toggleBackground(self):
        if render.isHidden():
            render.show()
        else:
            render.hide()
        if self.book.isBackgroundHidden():
            self.book.show()
            self.book.setBackgroundHidden(False)
        else:
            self.book.hide()
            self.book.setBackgroundHidden(True)

    def openKickPage(self):
        self.fsm.request('kickSection')

    def openSysMsgPage(self):
        self.fsm.request('sysMsgSection')

    def exitBasePage(self):
        self.systemMsgBtn.destroy()
        del self.systemMsgBtn
        self.idBtn.destroy()
        del self.idBtn
        self.kickBtn.destroy()
        del self.kickBtn
        self.bgBtn.destroy()
        del self.bgBtn
        self.ghostBtn.destroy()
        del self.ghostBtn
        self.oobeBtn.destroy()
        del self.oobeBtn
        self.tokenBtn.destroy()
        del self.tokenBtn
        self.worldBtn.destroy()
        del self.worldBtn
        self.allGagsBtn.destroy()
        del self.allGagsBtn
        self.allSlotsBtn.destroy()
        del self.allSlotsBtn
        self.physDbgBtn.destroy()
        del self.physDbgBtn
        self.analyzeBtn.destroy()
        del self.analyzeBtn
        if hasattr(self, 'analyzeDlg'):
            self.ignore('analyzedone')
            self.analyzeDlg.cleanup()
            del self.analyzeDlg
        self.directBtn.destroy()
        del self.directBtn
        self.listBtn.destroy()
        del self.listBtn
        self.pstatsBtn.destroy()
        del self.pstatsBtn

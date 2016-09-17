"""

  Filename: ChatInput.py
  Created by: blach (04Oct14)

"""

from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import *
from direct.fsm import ClassicFSM, State, StateData
from lib.coginvasion.globals import ChatGlobals
import random

class ChatInput(DirectObject, StateData.StateData):

    def __init__(self):
        DirectObject.__init__(self)
        StateData.StateData.__init__(self, 'chatInputDone')
        # Keys that can be pressed to trigger the chat input box.
        self.keyList = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                        "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
                        "y", "z", ",", ".", "/", ";", ":", '"', "'", "{", "}", "[",
                        "]", "-", "_", "+", "=", "<", ">", "?", "!", "`", "~", "@",
                        "#", "$", "%", "^", "&", "*", "(", ")", "5", "6", "7",
                        "8", "9", "0", "|"]
        self.keyToShiftKey = {"/": "?", "1": "!", "2": "@", "3": "#", "4": "$",
            "5": "%", "6": "^", "7": "&", "8": "*", "9": "(", "0": ")", "-": "_",
            "=": "+", "`": "~", "[": "{", "]": "}", "\\": "|", ";": ":", "'": "\"",
            ",": "<", ".": ">"}
        self.chat_btn_model = None
        self.chatBx = None
        self.chat_btn = None
        self.chatInput = None
        self.chatBx_send = None
        self.chatBx_close = None
        self.fsm = ClassicFSM.ClassicFSM('chatInput', [
                    State.State('off', self.enterOff, self.exitOff),
                    State.State('idle', self.enterIdle, self.exitIdle),
                    State.State('input', self.enterInput, self.exitInput)],
                    'off', 'off')
        self.fsm.enterInitialState()
        self.entered = False
        return

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enter(self):
        if self.entered:
            return
        StateData.StateData.enter(self)
        # Create the gui for chat input.
        self.chat_btn_model = loader.loadModel("phase_3.5/models/gui/chat_input_gui.bam")
        self.chatBx = self.chat_btn_model.find('**/Chat_Bx_FNL')
        self.chatBx.reparentTo(base.a2dTopLeft)
        self.chatBx.hide()
        self.chatBx.setBin('gui-popup', 60)
        self.chat_btn = DirectButton(text=("", "Chat", "Chat", ""), text_shadow=(0, 0, 0, 1),
                                    geom=(self.chat_btn_model.find('**/ChtBx_ChtBtn_UP'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_DN'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_RLVR')), relief=None,
                                    text_scale=0.0525, text_pos=(0, -0.08), text_fg=(1,1,1,1),
                                    command=self.openChatInput, pos=(0.085, 0, -0.075), scale=1.25,
                                    parent=base.a2dTopLeft, extraArgs=[""])
        self.chat_btn.setBin('gui-popup', 60)
        self.fsm.request('idle')
        self.entered = True

    def exit(self):
        StateData.StateData.exit(self)
        if self.chat_btn_model:
            self.chat_btn_model.removeNode()
            self.chat_btn_model = None
        if self.chatBx:
            self.chatBx.removeNode()
            self.chatBx = None
        if self.chat_btn:
            self.chat_btn.destroy()
            self.chat_btn = None
        self.disableKeyboardShortcuts()
        self.entered = False

    def enableKeyboardShortcuts(self):
        # Enable the shortcuts to open the chat box.
        for key in self.keyList:
            self.acceptOnce(key, self.openChatInput, [key])
            self.acceptOnce("shift-" + key, self.openChatInput, ["shift-" + key.upper()])

    def openChatInput(self, key):
        if "shift-" in key:
            _, keyName = key.split('-')
            key = self.keyToShiftKey.get(keyName, None)
            if not key:
                key = keyName.upper()
        self.fsm.request('input', [key])

    def disableKeyboardShortcuts(self):
        # Disable the shortcuts to open the chat box.
        for key in self.keyList:
            self.ignore(key)
            self.ignore("shift-" + key)

    def enterInput(self, key, command = None, extraArgs = []):
        if base.localAvatar.invGui:
            base.localAvatar.invGui.disableWeaponSwitch()
        
        if command == None:
            command = self.sendChat
        if not self.chatBx:
            base.localAvatar.disableChatInput()
            base.localAvatar.createChatInput()
            self.fsm.request('input', [''])
            return
        self.chatBx.show()
        self.chatBx.setScale(1.20)
        self.chatBx.setPos(0.30, 0, -0.245)
        self.chatBx_close = DirectButton(text=("", "Cancel", "Cancel", ""), text_shadow=(0, 0, 0, 1),
                                                geom=(self.chat_btn_model.find('**/CloseBtn_UP'),
                                                self.chat_btn_model.find('**/CloseBtn_DN'),
                                                self.chat_btn_model.find('**/CloseBtn_Rllvr')), relief=None,
                                                text_scale=0.0525, text_pos=(0, -0.08), text_fg=(1,1,1,1), parent=self.chatBx,
                                                pos=(-0.15, 0, -0.0875), scale=1.05, command=self.fsm.request, extraArgs = ['idle'])
        self.chatInput = DirectEntry(focus=1, cursorKeys=0, relief=None, geom=None, numLines=3,
                                parent=self.chatBx, pos=(-0.2, 0, 0.11), scale=0.05, command=command,
                                width=8.6, initialText=key, backgroundFocus = 0, extraArgs = extraArgs)
        self.chatBx_send = DirectButton(text=("", "Say It", "Say It", ""), text_shadow=(0, 0, 0, 1),
                                    geom=(self.chat_btn_model.find('**/ChtBx_ChtBtn_UP'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_DN'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_RLVR')), relief=None,
                                    text_scale=0.0525, text_pos=(0, -0.08), text_fg=(1,1,1,1),
                                    parent=self.chatBx, scale=1.05, command=command,
                                    pos=(0.18, 0, -0.0875), extraArgs=[self.chatInput.get()] + extraArgs)
        self.chatBx_close.setBin('gui-popup', 60)
        self.chatBx_send.setBin('gui-popup', 60)
        self.chatInput.setBin('gui-popup', 60)

    def sendChat(self, chat):
        chat = self.chatInput.get()
        if hasattr(base, 'localAvatar'):
            if len(chat) > 0:
                base.localAvatar.b_setChat(chat)
        self.fsm.request('idle')

    def exitInput(self):
        if base.localAvatar.invGui:
            base.localAvatar.invGui.enableWeaponSwitch()
        if self.chatBx:
            self.chatBx.hide()
        if self.chatBx_close:
            self.chatBx_close.destroy()
            self.chatBx_close = None
        if self.chatBx_send:
            self.chatBx_send.destroy()
            self.chatBx_send = None
        if self.chatInput:
            self.chatInput.destroy()
            self.chatInput = None

    def enterIdle(self):
        if self.chat_btn:
            self.chat_btn.show()
        self.enableKeyboardShortcuts()

    def exitIdle(self):
        if self.chat_btn:
            self.chat_btn.hide()
        self.disableKeyboardShortcuts()

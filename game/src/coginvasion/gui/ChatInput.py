"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ChatInput.py
@author Brian Lach
@date October 04, 2014

"""

from panda3d.core import TextNode

from direct.gui.DirectGui import *
from direct.showbase.DirectObject import *
from direct.fsm import ClassicFSM, State, StateData

from src.coginvasion.globals import ChatGlobals

import string

# Messenger events
CHAT_WINDOW_OPENED_EVENT = 'chatWindowOpened'
CHAT_WINDOW_CLOSED_EVENT = 'chatWindowClosed'

class ChatInput(DirectObject, StateData.StateData):

    def __init__(self):
        DirectObject.__init__(self)
        StateData.StateData.__init__(self, 'chatInputDone')

        # Keys that can be pressed to trigger the chat input box.
        self.setKeyList()
        
        self.keyToShiftKey = {"/": "?", "1": "!", "2": "@", "3": "#", "4": "$",
            "5": "%", "6": "^", "7": "&", "8": "*", "9": "(", "0": ")", "-": "_",
            "=": "+", "`": "~", "[": "{", "]": "}", "\\": "|", ";": ":", "'": "\"",
            ",": "<", ".": ">"}
        
        # Loads the sfx that plays when the input window is opened.
        self.chatSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_quicktalker.ogg')
        self.chatSfx.setVolume(0.5)
        
        # Loads the sfx that plays when the user tries to input text with non-ASCII characters.
        self.badInputSfx = loader.loadSfx('phase_4/audio/sfx/ring_miss.ogg')
        self.badInputSfx.setVolume(0.5)

        self.chatFrame = None
        
        self.chat_btn_model = None
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
        self.badInputPresent = False
        return
    
    def setKeyList(self):
        # Sets the key list. Should be called after controls are updated.
        # Uses the extremely useful 'string' class.
        # Refer to: https://docs.python.org/3.4/library/string.html
        keys = list(string.printable[5:94])
        
        for control in base.inputStore.getControls():
            # We don't want keys that are assigned to another control to
            # open up the chat input GUI.
            if not control is base.inputStore.Chat:
                key = control[1].current
                
                if key in keys:
                    # This will remove every control that isn't the open chat control.
                    keys.remove(key)

        self.keyList = keys

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
        gui = self.chat_btn_model
        self.chatFrame = DirectFrame(parent = base.a2dTopLeft, image = gui.find("**/Chat_Bx_FNL"),
                                     relief = None, pos = (0.24, 0, -0.194), state = DGG.NORMAL,
                                     sortOrder = DGG.FOREGROUND_SORT_INDEX)
        self.chatFrame.hide()
        self.chat_btn = DirectButton(text=("", "Chat", "Chat", ""), text_shadow=(0, 0, 0, 1),
                                    geom=(self.chat_btn_model.find('**/ChtBx_ChtBtn_UP'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_DN'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_RLVR')), relief=None,
                                    text_scale=0.06, text_pos=(-0.0525, -0.09), text_fg=(1,1,1,1),
                                    command=self.openChatInput, pos=(0.0683, 0, -0.072), scale=1.179,
                                    text_align = TextNode.ALeft, sortOrder=DGG.FOREGROUND_SORT_INDEX,
                                    parent=base.a2dTopLeft, extraArgs=[""])
        self.fsm.request('idle')
        self.entered = True

    def exit(self):
        StateData.StateData.exit(self)
        if self.chat_btn_model:
            self.chat_btn_model.removeNode()
            self.chat_btn_model = None
        if self.chatFrame:
            self.chatFrame.removeNode()
            self.chatFrame = None
        if self.chat_btn:
            self.chat_btn.destroy()
            self.chat_btn = None
        self.disableKeyboardShortcuts()
        self.entered = False

    def enableKeyboardShortcuts(self):
        # Enable the shortcuts to open the chat box.
        if base.localAvatarReachable():
            if not base.localAvatar.GTAControls:
                for key in self.keyList:
                    self.acceptOnce(key, self.openChatInput, [key])
                    self.acceptOnce("shift-" + key, self.openChatInput, ["shift-" + key.upper()])
            else:
                self.acceptOnce(base.inputStore.Chat, self.openChatInput, [""])
            base.localAvatar.enableGagKeys()

    def openChatInput(self, key):
        if "shift-" in key:
            _, keyName = key.split('-')
            key = self.keyToShiftKey.get(keyName, None)
            if not key:
                key = keyName.upper()
        
        self.fsm.request('input', [key])
        self.chatSfx.play()

    def disableKeyboardShortcuts(self):
        # Disable the shortcuts to open the chat box.
        if base.localAvatarReachable():
            if not base.localAvatar.GTAControls:
                for key in self.keyList:
                    self.ignore(key)
                    self.ignore('shift-' + key)
            else:
                self.ignore(base.inputStore.Chat)
            base.localAvatar.disableGagKeys()

    def enterInput(self, key, recipient = None):
        # Let's send our open chat window event.
        messenger.send(CHAT_WINDOW_OPENED_EVENT, [])

        if base.localAvatarReachable() and base.localAvatar.GTAControls:
            if hasattr(base.localAvatar, 'book_btn'):
                base.localAvatar.book_btn.hide()
            key = ""

        if not self.chatFrame:
            base.localAvatar.disableChatInput()
            base.localAvatar.createChatInput()
            self.fsm.request('idle', [])
            return
        self.chatFrame.show()
        self.chatBx_close = DirectButton(text=("", "Cancel", "Cancel", ""), text_shadow=(0, 0, 0, 1),
                                                geom=(self.chat_btn_model.find('**/CloseBtn_UP'),
                                                self.chat_btn_model.find('**/CloseBtn_DN'),
                                                self.chat_btn_model.find('**/CloseBtn_Rllvr')), relief=None,
                                                text_scale=0.06, text_pos=(0, -0.09), text_fg=(1,1,1,1), parent=self.chatFrame,
                                                pos=(-0.151, 0, -0.088), scale=1, command=self.fsm.request, extraArgs = ['idle'])
        self.chatInput = DirectEntry(focus=1, cursorKeys=0, relief=None, geom=None, numLines=3,
                                parent=self.chatFrame, pos=(-0.2, 0, 0.11), scale=0.05, command=self.sendChat,
                                width=8.6, initialText=key, backgroundFocus = 0, extraArgs = [recipient])
        self.chatInput.bind(DGG.OVERFLOW, self.sendChat, extraArgs = [recipient])
        self.chatInput.bind(DGG.TYPE, self.onTextChangeEvent, extraArgs = [])
        self.chatInput.bind(DGG.ERASE, self.onTextChangeEvent, extraArgs = [])
        self.chatBx_send = DirectButton(text=("", "Say It", "Say It", ""), text_shadow=(0, 0, 0, 1),
                                    geom=(self.chat_btn_model.find('**/ChtBx_ChtBtn_UP'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_DN'),
                                    self.chat_btn_model.find('**/ChtBx_ChtBtn_RLVR')), relief=None,
                                    text_scale=0.06, text_pos=(0, -0.09), text_fg=(1,1,1,1),
                                    parent=self.chatFrame, scale=1, command=self.sendChat,
                                    pos=(0.182, 0, -0.088), extraArgs=[recipient])
        self.chatBx_close.setBin('gui-popup', 60)
        self.chatBx_send.setBin('gui-popup', 60)
        self.chatInput.setBin('gui-popup', 60)
        
    def onTextChangeEvent(self, _):
        if self.chatInput:
            chat = self.chatInput.guiItem.getText()
            chat = chat.replace('\1red\1', '')
            chat = chat.replace('\2', '')
            newInput = list(chat)
            
            try:
                chat.decode('ascii')
            except UnicodeDecodeError:
                # Non-ASCII characters were entered.
                newText = ""
                validKeys = list(string.printable[5:94])
                for char in newInput:
                    if not len(char) == 0:
                        if not char in validKeys:
                            # Because TextProperties are broken, let's replace the char with a
                            # question mark.
                            newText += '?'
                            #newText += '\1red\1' + char + '\2'
                            continue
                    newText += char
                self.chatInput.guiItem.setText(newText)
                #self.badInputPresent = True
            else:
                self.badInputPresent = False

    def sendChat(self, _, recipient):
        chat = self.chatInput.get()
        if hasattr(base, 'localAvatar'):
            if len(chat) > 0 and not self.badInputPresent:
                # Using an underscore as a prefix will slant the text.
                if chat[0] == '_':
                    # Because TextProperties are broken, let's disable this.
                    # chat = '\1slant\1' + chat[1:]
                    chat = chat[1:]
                if recipient:
                    base.cr.friendsManager.d_sendWhisper(recipient, chat)
                    self.enableKeyboardShortcuts()
                else:
                    base.localAvatar.b_setChat(chat)
            elif self.badInputPresent:
                base.playSfx(self.badInputSfx)
                
        if not self.badInputPresent:
            self.fsm.request('idle')

    def exitInput(self):
        if base.localAvatarReachable() and base.localAvatar.GTAControls and hasattr(base.localAvatar, 'book_btn'):
            base.localAvatar.book_btn.show()
        if self.chatFrame:
            self.chatFrame.hide()
        if self.chatBx_close:
            self.chatBx_close.destroy()
            self.chatBx_close = None
        if self.chatBx_send:
            self.chatBx_send.destroy()
            self.chatBx_send = None
        if self.chatInput:
            self.chatInput.destroy()
            self.chatInput = None
        
        # This is for preventing the sending of non-ASCII characters.
        self.badInputPresent = False
            
        # Let's send our close chat window event.
        messenger.send(CHAT_WINDOW_CLOSED_EVENT, [])

    def enterIdle(self):
        if self.chat_btn:
            self.chat_btn.show()
        self.enableKeyboardShortcuts()

    def exitIdle(self):
        if self.chat_btn:
            self.chat_btn.hide()
        self.disableKeyboardShortcuts()

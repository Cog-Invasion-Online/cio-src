"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ChoiceWidget.py
@author Brian Lach
@date March 13, 2017

"""

from panda3d.core import TextNode

from direct.gui.DirectGui import DirectFrame, OnscreenText, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals

DISABLED_COLOR = (0.45, 0.45, 0.45, 1)
DESC_BACKGROUND_COLOR = (0.70, 0.70, 0.70, 1.0)
AUTO = 1
MULTICHOICE = 2
DEGREE = 3
INDEX = 4

class ChoiceWidget(DirectFrame):
    notify = directNotify.newCategory("ChoiceWidget")

    def __init__(self, parent, options, pos = (0, 0, 0), command = None, 
            widgetName = "", choiceTextScale = 0.08, desc = "",
            settingKeyName = None, mode = AUTO, requirement = None):
        """ 
        Generates an ordered choice widget with the specified parameters.
        
        Parameters:
        
        parent: Pretty much self-explanatory, this is the parent of the widget.
        If an object with a `book` attribute is passed in, it will use that instead.
        
        options: A list of options that the user can select with the GUI.
        
        pos: Pretty much self-explanatory.
        
        command: Function that should be executed whenever a game setting is updated.
        The newly saved choice is passed to the specified function.
        
        widgetName: The label shown to the left of the widget identifying what the widget
        is for.
        
        choiceTextScale: The scale of the text which displays which option the user has
        currently selected.
        
        desc: Optional description of what the choices displayed by this widget are for.
        
        settingKeyName: The name of the key inside of the game settings map that this choice
        widget works with. This MUST be set if trying to simulate a game setting changer widget.
        
        mode: This is the kind of widget this is going to be. Use one of the following:
            - AUTO:
                - The system will attempt to figure out what the type of choices are available.
                    * 2 options automatically looks like a true/false widget *
            - MULTICHOICE:
                - This overrides the system in case there are two options but true/false functionality
                isn't wanted.
            - DEGREE:
                - This means that the choice widget deals with x in front of some sort of degree value that should
                - be stripped away when selecting choices. This is used for the antialiasing choice widget.
        
        """
        self.requirement = requirement
        self.options = options
        self.command = command
        self.currentChoiceIndex = 0
        self.origChoice = None
        self.userChoice = None
        self.settingKeyName = settingKeyName
        self.mode = mode
        
        # Let's update the options if we specified a setting key name.
        if self.settingKeyName and len(self.settingKeyName) > 0:
            settingsMgr = CIGlobals.getSettingsMgr()
            settingInst = settingsMgr.getSetting(self.settingKeyName)
            
            if not settingInst:
                raise ValueError("Setting \"%s\" could not be found!")
            else:
                self.options = settingInst.getOptions()
                desc = settingInst.getDescription()
        
        widgetParent = parent
        if hasattr(parent, 'book'):
            widgetParent = parent.book
        
        DirectFrame.__init__(self, parent = widgetParent, pos = pos)
        
        bg = loader.loadModel('phase_3/models/gui/ChatPanel.bam')

        self.selFrame = DirectFrame(pos = (0.4, 0, 0), frameColor = (1.0, 1.0, 1.0, 1.0), image = bg, relief = None, 
            image_scale = (0.22, 0.11, 0.11), 
            image_pos = (-0.107, 0.062, 0.062), 
        parent = self)

        self.choiceText = OnscreenText(text = "Hello!", align = TextNode.ACenter, parent = self.selFrame, pos = (0, -0.01), scale = choiceTextScale)
        self.fwdBtn = CIGlobals.makeDirectionalBtn(1, self.selFrame, pos = (0.2, 0, 0), command = self.__goFwd)
        self.bckBtn = CIGlobals.makeDirectionalBtn(0, self.selFrame, pos = (-0.2, 0, 0), command = self.__goBck)

        self.lbl = OnscreenText(text = widgetName + ":", pos = (-0.7, 0, 0), align = TextNode.ALeft, parent = self)
        
        if len(desc) > 0:
            self.desc = OnscreenText(text = desc, pos = (0.0, -0.1, 0.0), parent = self.selFrame, 
                scale = 0.05, bg = DESC_BACKGROUND_COLOR, mayChange = False)
            self.desc.setBin('gui-popup', 40)
            self.desc.hide()
            
            # Let's bind our events on the selection frame for the description.
            self.selFrame['state'] = DGG.NORMAL
            self.selFrame.bind(DGG.ENTER, self.__setDescVisible, extraArgs = [True])
            self.selFrame.bind(DGG.EXIT, self.__setDescVisible, extraArgs = [False])

        self.initialiseoptions(ChoiceWidget)

        self.reset()

        bg.detachNode()
        del bg
        
    def reset(self):
        """ Resets the selected choice to the very first option, or, if representing choices for a game setting,
        resets the widget to the currently saved setting. """ 
        
        # The index of the original display choice.
        destIndex = 0

        if self.settingKeyName:
            # This widget is supposed to be used to change game settings. Let's lookup the currently saved game setting.
            self.origChoice = self.__getCurrentSetting().getValue()
            
            try:
                if self.mode == DEGREE and not self.origChoice == 0:
                    destIndex = self.options.index('x{0}'.format(str(self.origChoice)))
                elif (self.mode == AUTO and len(self.options) == 2) or isinstance(self.origChoice, (int, long)):
                    destIndex = int(self.origChoice)
                elif isinstance(self.origChoice, (list, tuple)):
                    destIndex = self.options.index('{0}x{1}'.format(str(self.origChoice[0]), str(self.origChoice[1])))
                elif self.origChoice in self.options:
                    destIndex = self.options.index(self.origChoice)
                elif self.origChoice.title() in self.options:
                    destIndex = self.options.index(self.origChoice.title())
            except:
                # We couldn't determine the right index for the original choice. Let's ignore any errors and default
                # to the very first choice when we reset.
                pass
        else:
            # If this widget is not being used to simulate changing game settings, let's use the first value in options as the original choice.
            self.origChoice = self.options[0]
        self.userChoice = self.origChoice
        self.goto(destIndex)
        
    def saveSetting(self):
        """ If `settingKeyName` was set, this updates the game setting key with the choice selected with the widget. However, 
        if `settingKeyName` was not set, it will send the command specified with the current user choice. """
        willUpdateChoice = (self.userChoice != self.origChoice)
        if self.settingKeyName and willUpdateChoice:
            settingInst = CIGlobals.getSettingsMgr().getSetting(self.settingKeyName)
            
            if settingInst:
                settingInst.setValue(self.userChoice)

            self.reset()
            
        if self.command and willUpdateChoice:
            # Let's send the command with the newly saved choice.
            self.command(self.userChoice)
        
    def __getCurrentSetting(self):
        return CIGlobals.getSettingsMgr().getSetting(self.settingKeyName)
        
    def __setDescVisible(self, visible, _):
        if visible:
            CIGlobals.getRolloverSound().play()
            self.desc.show()
        else:
            self.desc.hide()

    def cleanup(self):
        if hasattr(self, 'choiceText'):
            self.choiceText.destroy()
            del self.choiceText
        if hasattr(self, 'fwdBtn'):
            self.fwdBtn.destroy()
            del self.fwdBtn
        if hasattr(self, 'bckBtn'):
            self.bckBtn.destroy()
            del self.bckBtn
        if hasattr(self, 'lbl'):
            self.lbl.destroy()
            del self.lbl
        if hasattr(self, 'selFrame'):
            self.selFrame.destroy()
            del self.selFrame
        if hasattr(self, 'desc'):
            self.desc.destroy()
            del self.desc
        del self.options
        del self.command
        del self.currentChoiceIndex
        del self.settingKeyName
        del self.origChoice
        del self.userChoice
        del self.mode
        del self.requirement
        self.destroy()

    def goto(self, index):
        self.currentChoiceIndex = index
        self.updateDirectionalBtns()
        self.__setCurrentData(False)

    def __setCurrentData(self, doCmd = True):
        self.choiceText.setText(self.options[self.currentChoiceIndex])
        if (doCmd):
            
            # Let's update the internal user choice.
            if self.mode == AUTO and len(self.options) == 2:
                # If we only have two options, we must be working with on/off choices.
                self.userChoice = bool(self.currentChoiceIndex)
            elif self.mode == INDEX:
                self.userChoice = self.currentChoiceIndex
            elif self.mode == DEGREE or 'x' in self.choiceText.getText():
                # We're working with either a degree based option or a resolution option.
                data = self.options[self.currentChoiceIndex].split('x')
                
                if CIGlobals.isEmptyString(data[0]):
                    # This is a degree-based option.
                    if self.currentChoiceIndex != 0:
                        self.userChoice = int(data[1])
                    else:
                        self.userChoice = 0
                else:
                    # This is a screen resolution option.
                    self.userChoice = (int(data[0]), int(data[1]))
            else:
                self.userChoice = self.options[self.currentChoiceIndex]

    def updateDirectionalBtns(self):
        if self.requirement and callable(self.requirement):
            if not self.requirement():
                # The requirement to modify this choice widget was not met.
                for btn in [self.fwdBtn, self.bckBtn]:
                    btn['state'] = DGG.DISABLED
                    btn.setColorScale(DISABLED_COLOR)
                return

        self.fwdBtn['state'] = DGG.NORMAL
        self.bckBtn['state'] = DGG.NORMAL
        self.fwdBtn.setColorScale(1, 1, 1, 1)
        self.bckBtn.setColorScale(1, 1, 1, 1)
        if self.currentChoiceIndex == 0:
            self.bckBtn['state'] = DGG.DISABLED
            self.bckBtn.setColorScale(DISABLED_COLOR)
        elif self.currentChoiceIndex == len(self.options) - 1:
            self.fwdBtn['state'] = DGG.DISABLED
            self.fwdBtn.setColorScale(DISABLED_COLOR)

    def __goFwd(self):
        if self.currentChoiceIndex < len(self.options) - 1:
            self.currentChoiceIndex += 1
            self.__setCurrentData()
        self.updateDirectionalBtns()

    def __goBck(self):
        if self.currentChoiceIndex > 0:
            self.currentChoiceIndex -= 1
            self.__setCurrentData()
        self.updateDirectionalBtns()

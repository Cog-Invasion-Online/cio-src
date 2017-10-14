"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BackpackGUI.py
@author Brian Lach
@date September 20, 2015

"""

from panda3d.core import Vec4, TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DGG, DirectButton, DirectFrame, OnscreenText
from direct.fsm import ClassicFSM, State

from src.coginvasion.gags import GagGlobals, GagManager
from src.coginvasion.globals import CIGlobals

TrackZValueByName = {GagGlobals.ToonUp : 0.4,
                     GagGlobals.Trap : 0.29,
                     GagGlobals.Lure : 0.18,
                     GagGlobals.Sound : 0.07,
                     GagGlobals.Throw : -0.04,
                     GagGlobals.Squirt : -0.15,
                     GagGlobals.Drop : -0.26}
GagButtonXValues = [-0.38,
                    -0.2,
                    -0.02,
                    0.16,
                    0.34,
                    0.52,
                    0.7]

class BackpackGUI(DirectFrame):
    notify = directNotify.newCategory('BackpackGUI')
    InLoadoutColor = Vec4(1, 0.6, 0.5, 1)
    DefaultColor = Vec4(0, 0.6, 1, 1)
    DisabledColor = Vec4(0.5, 0.5, 0.5, 1)

    def __init__(self):
        DirectFrame.__init__(self)
        self.trackByName = {}
        self.gagButtonByName = {}
        self.editButton = None
        self.slotsText = None
        self.fsm = ClassicFSM.ClassicFSM('BackpackGUI', [State.State('off', self.enterOff, self.exitOff),
         State.State('idle', self.enterIdle, self.exitIdle),
         State.State('edit', self.enterEditGags, self.exitEditGags)], 'off', 'off')
        self.fsm.enterInitialState()
        self.editFSM = ClassicFSM.ClassicFSM('BPGUIEdit', [State.State('off', self.enterOff, self.exitOff),
         State.State('add', self.enterAddGags, self.exitAddGags),
         State.State('remove', self.enterRemoveGags, self.exitRemoveGags)], 'off', 'off')
        self.editFSM.enterInitialState()
        self.gm = GagManager.GagManager()
        self.numSlots = base.localAvatar.getNumGagSlots()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def __addGagToLoadout(self, gagName):
        gagId = GagGlobals.gagIdByName[gagName]
        self.newLoadout.append(gagId)
        self.__updateButtons_add()

    def __removeGagFromLoadout(self, gagName):
        gagId = GagGlobals.gagIdByName[gagName]
        self.newLoadout.remove(gagId)
        self.__updateButtons_remove()

    def __updateButtons_add(self):
        for gagName, button in self.gagButtonByName.items():
            if self.isInLoadoutNew(gagName):
                button['state'] = DGG.DISABLED
                button['image_color'] = self.InLoadoutColor
            elif len(self.newLoadout) == self.numSlots:
                button['state'] = DGG.DISABLED
                button['image_color'] = self.DisabledColor
            else:
                button['state'] = DGG.NORMAL
                button['command'] = self.__addGagToLoadout
                button['extraArgs'] = [gagName]
                button['image_color'] = self.DefaultColor

    def __updateButtons_remove(self):
        for gagName, button in self.gagButtonByName.items():
            if self.isInLoadoutNew(gagName):
                button['state'] = DGG.NORMAL
                button['command'] = self.__removeGagFromLoadout
                button['extraArgs'] = [gagName]
                button['image_color'] = self.InLoadoutColor
            else:
                button['state'] = DGG.DISABLED
                button['image_color'] = self.DisabledColor

    def enterAddGags(self):
        self.switchButton['text'] = 'Remove Gags'
        self.switchButton['command'] = self.editFSM.request
        self.switchButton['extraArgs'] = ['remove']
        self.__updateButtons_add()

    def exitAddGags(self):
        pass

    def enterRemoveGags(self):
        self.switchButton['text'] = 'Add Gags'
        self.switchButton['command'] = self.editFSM.request
        self.switchButton['extraArgs'] = ['add']
        self.__updateButtons_remove()

    def exitRemoveGags(self):
        pass

    def enterEditGags(self):
        self.initialLoadout = []
        for instance in base.localAvatar.backpack.getLoadout():
            self.initialLoadout.append(instance.getID())
        self.newLoadout = list(self.initialLoadout)
        self.editButton['text'] = 'Stop Editing'
        self.editButton['command'] = self.fsm.request
        self.editButton['extraArgs'] = ['idle']
        self.switchButton = DirectButton(relief = None,
         image = CIGlobals.getDefaultBtnGeom(),
         text = 'Add Gags',
         text_scale = 0.045,
         text_pos = (0, -0.01),
         pos = (0.5, 0, -0.4))
        self.editFSM.request('add')

    def exitEditGags(self):
        self.switchButton.destroy()
        del self.switchButton
        if len(self.newLoadout) > 0 and len(self.newLoadout) <= self.numSlots:
            base.localAvatar.sendUpdate('requestSetLoadout', [self.newLoadout])
        del self.newLoadout
        del self.initialLoadout

    def isInLoadoutNew(self, gagName):
        gagId = GagGlobals.gagIdByName[gagName]
        return gagId in self.newLoadout

    def isInLoadoutLive(self, gagName):
        for instance in base.localAvatar.backpack.getLoadout():
            if instance.getName() == gagName:
                return True
        return False

    def enterIdle(self):
        self.editButton['text'] = 'Edit Loadout'
        self.editButton['command'] = self.fsm.request
        self.editButton['extraArgs'] = ['edit']
        for gagName, button in self.gagButtonByName.items():
            button['state'] = DGG.DISABLED
            if self.isInLoadoutLive(gagName):
                button['image_color'] = self.InLoadoutColor
            else:
                button['image_color'] = self.DefaultColor

    def exitIdle(self):
        pass

    def __makeTrack(self, trackName):
        gui = loader.loadModel('phase_3.5/models/gui/inventory_gui.bam')
        color = GagGlobals.TrackColorByName[trackName]
        track = gui.find('**/InventoryRow')
        track.setColor(*color)
        frame = DirectFrame(parent = self)
        frame.setZ(TrackZValueByName[trackName])
        frame['image'] = track
        trackTitle = OnscreenText(text = trackName, parent = frame, pos = (-0.63, -0.01, 0), scale = 0.06)
        self.trackByName[trackName] = frame

    def __makeGagButton(self, gagName, trackName):
        gui = loader.loadModel('phase_3.5/models/gui/inventory_gui.bam')
        icons = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam')
        icon = icons.find(GagGlobals.InventoryIconByName[gagName])
        index = GagGlobals.TrackGagNamesByTrackName[trackName].index(gagName)
        xValue = GagButtonXValues[index]
        button = DirectButton(relief = None, image = (gui.find('**/InventoryButtonUp'),
         gui.find('**/InventoryButtonDown'),
         gui.find('**/InventoryButtonRollover'),
         gui.find('**/InventoryButtonFlat')),
         geom = icon, geom_scale = 0.6, parent = self.trackByName[trackName],
         text = str(base.localAvatar.getBackpack().getSupply(gagName)), text_align = TextNode.ARight, text_scale = 0.04,
         text_fg=Vec4(1, 1, 1, 1), text_pos=(0.07, -0.04))
        button.setX(xValue)
        self.gagButtonByName[gagName] = button

    def createGUI(self):
        for i in xrange(len(GagGlobals.TrackNameById)):
            trackName = GagGlobals.TrackNameById[i]
            self.__makeTrack(trackName)
            for j in xrange(len(GagGlobals.TrackGagNamesByTrackName[trackName])):
                gagName = GagGlobals.TrackGagNamesByTrackName[trackName][j]
                gagId = GagGlobals.gagIdByName[gagName]
                if base.localAvatar.getBackpack().hasGag(gagId):
                    self.__makeGagButton(gagName, trackName)
        self.editButton = DirectButton(relief = None,
         image = CIGlobals.getDefaultBtnGeom(),
         text = 'Edit Loadout',
         text_scale = 0.045,
         text_pos = (0, -0.01),
         pos = (-0.5, 0, -0.4))
        self.slotsText = OnscreenText(text = "Slots Unlocked: %d" % self.numSlots, pos = (0, -0.6))
        self.fsm.request('idle')

    def deleteGUI(self):
        self.editFSM.requestFinalState()
        self.fsm.requestFinalState()
        if self.slotsText:
            self.slotsText.destroy()
            self.slotsText = None
        for button in self.gagButtonByName.values():
            button.destroy()
        self.gagButtonByName = None
        for track in self.trackByName.values():
            track.destroy()
        self.trackByName = None
        self.editButton.destroy()
        self.editButton = None
        self.gm = None
        del self.editFSM
        del self.fsm

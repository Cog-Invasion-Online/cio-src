"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SliderWidget.py
@author Brian Lach
@date March 13, 2017

"""

from pandac.PandaModules import TextNode

from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectSlider, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

class SliderWidget(DirectFrame):
    notify = directNotify.newCategory("SliderWidget")

    def __init__(self, page, widgetname, slrange, slcommand, pos = (0, 0, 0)):
        DirectFrame.__init__(self, parent = page.book, pos = pos)

        self.page = page

        self.text = OnscreenText(text = widgetname + ":", pos = (-0.7, 0, 0), align = TextNode.ALeft, parent = self)
        self.slider = DirectSlider(range=slrange, pageSize=0.1, command=slcommand, scale=0.3,
                                        orientation=DGG.HORIZONTAL, pos=(0.35, 0, 0.025), parent = self)
        self.valText = OnscreenText(text = "", pos = (0.7, -0.005, -0.005), align = TextNode.ALeft, parent = self)

    def setValText(self, text):
        self.valText.setText(text)

    def getSliderVal(self):
        return self.slider['value']

    def setSliderVal(self, val):
        self.slider['value'] = val

    def cleanup(self):
        if hasattr(self, 'text'):
            self.text.destroy()
            del self.text
        if hasattr(self, 'slider'):
            self.slider.destroy()
            del self.slider
        if hasattr(self, 'valText'):
            self.valText.destroy()
            del self.valText
        del self.page
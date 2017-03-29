"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CategoryTab.py
@author Brian Lach
@date 2017-03-13

"""

from pandac.PandaModules import TextNode, Vec4

from direct.gui.DirectGui import DirectButton
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals

class CategoryTab(DirectButton):
    notify = directNotify.newCategory("CategoryTab")

    normalColor = (1, 1, 1, 1)
    clickColor = (0.8, 0.8, 0, 1)
    rolloverColor = (0.15,0.82, 1.0, 1)
    disabledColor = (1, 0.98,0.15, 1)

    def __init__(self, page, text, extraArgs, pos = (0, 0, 0)):
        self.page = page

        gui = loader.loadModel('phase_3.5/models/gui/fishingBook.bam')

        DirectButton.__init__(self, parent = page.tabsFrame, relief = None, extraArgs = extraArgs, text = text, text_scale = 0.07,
                              text_align = TextNode.ALeft, text_pos = (0.07, 0.0, 0.0), image = gui.find('**/tabs/polySurface1'),
                              image_pos = (0.6, 1, -0.91), image_hpr = (0, 0, -90), image_scale = (0.033, 0.033, 0.035),
                              image_color = self.normalColor, image1_color = self.clickColor, image2_color = self.rolloverColor,
                              image3_color = self.disabledColor, text_fg = Vec4(0.2, 0.1, 0, 1), command = self.page.pickCategory, pos = pos,
                              rolloverSound = CIGlobals.getRolloverSound(), clickSound = CIGlobals.getClickSound())

        self.initialiseoptions(CategoryTab)
########################################
# Filename: RewardPanel.py
# Created by: DecodedLogic (31Jul16)
########################################
# There's some code similarities in here
# with the TTO for the panel because the
# panel is supposed to be similar.
########################################
#  Copyright Cog Invasion Online 2016  #
#    Codebase by Maverick and Brian    #
#                                      #
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectLabel, DGG

from lib.coginvasion.globals import CIGlobals

FRAME_SCALE = (1.75, 1, (0.75 * 1.1))
FRAME_POS = (0, 0, 0.587)
GEOM_POS = (0, 0, -0.05)

class RewardPanel(DirectFrame):
    notify = directNotify.newCategory('RewardPanel')
    
    def __init__(self, name):
        DirectFrame.__init__(self, relief = None, geom = DGG.getDefaultDialogGeom(), 
            geom_color = CIGlobals.DialogColor, geom_pos = GEOM_POS, geom_scale = FRAME_SCALE, 
        pos = FRAME_POS)
        self.initialiseoptions(RewardPanel)
        
        # Let's create the elements of the RewardPanel
        self.avNameLabel = DirectLabel(parent = self, relief = None, pos = (0, 0, 0.3), text = name, 
            text_scale = 0.08)
        
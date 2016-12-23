# Filename: MinigameUtils.py
# Created by:  blach (18Apr16)
#
# Helper methods for minigames.

from direct.gui.DirectGui import OnscreenImage

def getCrosshair(scale = 0.04, color = (1, 1, 1, 1), hidden = True):
    crosshair = OnscreenImage(image = "phase_4/maps/crosshair.png", scale = scale, color = color)
    crosshair.setTransparency(True)
    if hidden:
        crosshair.hide()
    return crosshair



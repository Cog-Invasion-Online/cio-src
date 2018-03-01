from direct.gui.DirectGui import DirectFrame

class Crosshair(DirectFrame):

    def __init__(self):
        DirectFrame.__init__(self, parent = aspect2d)
        self['image'] = 'phase_4/maps/crosshair_2.png'
        self['image_scale'] = 0.2
        self.setTransparency(True)
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *
from lib.coginvasion.globals import CIGlobals
base = ShowBase()

themap = loader.loadModel('phase_3.5/models/gui/toontown_map.bam')
#themap.reparentTo(aspect2d)
#themap.setSx(1.25)

frame = DirectFrame(parent=aspect2d, relief=None, image=themap, image_scale=(1.8, 1, 1.35), scale=0.97, pos=(0, 0, 0.0775))

cloudpos = [[(-0.61, 0, 0.18), (0.55, 0.25, 0.37), (180, 0, 0)],
            [(-0.54, 0, 0.34), (0.76, 0.4, 0.55), (180, 0, 0)],
            [(-0.55, 0, -0.09), (0.72, 0.4, 0.55), (0, 0, 0)],
            [(-0.67, 0, -0.51),  (0.5, 0.29, 0.38), (180, 0, 0)],
            [(-0.67, 0, 0.51), (0.50, 0.29, 0.38), (0, 0, 0)],
            [(0.67, 0, 0.51), (0.5, 0.29, 0.38), (0, 0, 0)],
            [(0.35, 0, -0.46),  (0.63, 0.35, 0.45), (0, 0, 0)],
            [(0.18, 0, -0.45),  (0.52, 0.27, 0.32), (0, 0, 0)],
            [(0.67, 0, -0.44),  (0.63, 0.35, 0.48), (180, 0, 0)]]
hoodclouds = [#[(0.02, 0, -0.17),  (0.63, 0.35, 0.48), (180, 0, 0), CIGlobals.ToontownCentral],
              [(0.63, 0, -0.13),  (0.63, 0.35, 0.40), (0, 0, 0), CIGlobals.DonaldsDock],
              [(0.51, 0, 0.25),  (0.57, 0.35, 0.40), (0, 0, 0), CIGlobals.TheBrrrgh],
              [(0.03, 0, 0.19),  (0.63, 0.35, 0.40), (180, 0, 0), CIGlobals.MinniesMelodyland],
              [(-0.08, 0, 0.46),  (0.54, 0.35, 0.40), (0, 0, 0), CIGlobals.DonaldsDreamland],
              [(-0.28, 0, -0.49),  (0.60, 0.35, 0.45), (0, 0, 0), CIGlobals.DaisyGardens]]
clouds = []

for pos, scale, hpr in cloudpos:
    cloud = loader.loadModel('phase_3.5/models/gui/cloud.bam')
    cloud.reparentTo(frame)
    cloud.setPos(pos)
    cloud.setScale(scale)
    cloud.setHpr(hpr)
    clouds.append(cloud)

for pos, scale, hpr, hood in hoodclouds:
    cloud = loader.loadModel('phase_3.5/models/gui/cloud.bam')
    cloud.reparentTo(frame)
    cloud.setPos(pos)
    cloud.setScale(scale)
    cloud.setHpr(hpr)
    clouds.append(cloud)

labeldata = [[(0, 0, -0.2), CIGlobals.ToontownCentral],
             [(0.65, 0, -0.125), CIGlobals.DonaldsDock],
             [(0.07, 0, 0.18), CIGlobals.MinniesMelodyland],
             [(-0.1, 0, 0.45), CIGlobals.DonaldsDreamland],
             [(0.5, 0, 0.25), CIGlobals.TheBrrrgh],
             [(-0.37, 0, -0.525), CIGlobals.DaisyGardens]]
fullname = 'Go Here'

for pos, name in labeldata:
    label = DirectButton(
        parent=frame,
        relief=None,
        pos=pos,
        pad=(0.2, 0.16),
        text=('', name, name),
        text_bg=Vec4(1, 1, 1, 0.4),
        text_scale=0.055,
        text_wordwrap=8,
        rolloverSound=None,
        clickSound=None,
        pressEffect=0,
        sortOrder=1,
        text_font = CIGlobals.getToonFont())
    label.resetFrameSize()

info = DirectLabel(relief = None, text = 'You are in: {0}\n{1}'.format('Toontown Central', 'Playground'),
                                     scale = 0.06, pos = (-0.4, 0, -0.74), parent = frame, text_align = TextNode.ACenter, text_font = CIGlobals.getToonFont())
#info.place()

btp = DirectButton(relief = None, text = "Back to Playground", geom = CIGlobals.getDefaultBtnGeom(), text_pos = (0, -0.018), geom_scale = (1.3, 1.11, 1.11), text_scale = 0.06, parent = frame, text_font = CIGlobals.getToonFont(), pos = (0.43, 0, -0.76))
#btp.place()	

#clouds[14].place()

base.run()

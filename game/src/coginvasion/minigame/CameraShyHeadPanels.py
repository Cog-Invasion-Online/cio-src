# Filename: CameraShyHeadPanels.py
# Created by:  blach (09Jul15)

from pandac.PandaModules import Point3, VBase4
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame

from src.coginvasion.toon.ToonHead import ToonHead
from HeadPanels import HeadPanels

class CameraShyHeadPanels(HeadPanels):
    notify = directNotify.newCategory('CameraShyHeadPanels')

    def __init__(self):
        HeadPanels.__init__(self)
        self.framePositions = [
            Point3(0.15, 0, -0.15),
            Point3(0.15, 0, -0.43),
            Point3(0.15, 0, -0.71),
            Point3(0.15, 0, -0.99)
        ]
        self.otherPlayerHeadHolderTransforms = {
            'scale': Point3(2, 1, 0.5),
            'pos': Point3(1.03, 0, 0)
        }
        self.otherPlayerHeadXValues = [
            -0.45,
            0,
            0.45
        ]
        self.state2Color = {
            0: VBase4(0.05, 0.05, 0.05, 1.0),
            1: VBase4(0.5, 0.5, 0.5, 1.0),
            2: VBase4(0.75, 0.75, 0.75, 1.0),
            3: VBase4(1.0, 1.0, 1.0, 1.0)
        }
        self.avId2otherPlayerAvIds2otherPlayerHeadsFrame = {}

    def generate(self, gender, head, headtype, color, doId, name):
        HeadPanels.generate(self, gender, head, headtype, color, doId, name, 0)

    def generateOtherPlayerGui(self):
        for avId in self.doId2Frame.keys():
            self.avId2otherPlayerAvIds2otherPlayerHeadsFrame[avId] = {}
            headNumber = -1
            frame = self.doId2Frame[avId][0]
            otherPlayerHeadsFrame = DirectFrame(relief = None, scale = 0.85, parent = frame)
            otherPlayerHeadsFrame['image'] = frame['image']
            otherPlayerHeadsFrame['image_color'] = frame['image_color']
            otherPlayerHeadsFrame['image_scale'] = self.otherPlayerHeadHolderTransforms['scale']
            otherPlayerHeadsFrame.setPos(self.otherPlayerHeadHolderTransforms['pos'])
            otherPlayerHeadsFrame.setBin('gui-popup', 70)
            self.frameList.append(otherPlayerHeadsFrame)
            for otherAvId in self.doId2Frame.keys():
                if otherAvId != avId:
                    headNumber += 1
                    otherAv = base.cr.doId2do.get(otherAvId)
                    gender = otherAv.getGender()
                    head, color = otherAv.getHeadStyle()
                    animal = otherAv.getAnimal()

                    headFrame = otherPlayerHeadsFrame.attachNewNode('otherPlayerHeadFrame')
                    headFrame.setPosHprScale(self.otherPlayerHeadXValues[headNumber], 5, -0.1, 180, 0, 0, 0.2, 0.2, 0.2)
                    headFrame.setColorScale(self.state2Color[0])
                    toon = ToonHead(None)
                    toon.generateHead(gender, animal, head)
                    r, g, b, _ = color
                    color = (r, g, b, 1.0)
                    toon.setHeadColor(color)
                    toon.setDepthWrite(1)
                    toon.setDepthTest(1)
                    toon.reparentTo(headFrame)

                    self.avId2otherPlayerAvIds2otherPlayerHeadsFrame[avId][otherAvId] = headFrame

    def updateOtherPlayerHead(self, avId, otherPlayerAvId, state):
        frame = self.avId2otherPlayerAvIds2otherPlayerHeadsFrame[avId][otherPlayerAvId]
        frame.setColorScale(self.state2Color[state])

    def delete(self):
        self.otherPlayerHeadHolderTransforms = None
        self.otherPlayerHeadXValues = None
        self.state2Color = None
        self.avId2otherPlayerAvIds2otherPlayerHeadsFrame = None
        HeadPanels.delete(self)

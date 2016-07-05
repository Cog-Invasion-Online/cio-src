"""

  Filename: LaffOMeter.py
  Created by: blach (??July14)

"""
from lib.coginvasion.base import ToontownIntervals

from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import Vec4

notify = directNotify.newCategory("LaffOMeter")

class LaffOMeter(DirectFrame):

    deathColor = Vec4(0.58039216, 0.80392157, 0.34117647, 1.0)

    def __init__(self, forRender = False):
        DirectFrame.__init__(self, relief=None, sortOrder=50, parent=base.a2dBottomLeft)
        self.initialiseoptions(LaffOMeter)
        self.container = DirectFrame(parent=self, relief=None)
        self.container.setBin('gui-popup', 60)

        if forRender:
            self.container.setY(0)
        self.forRender = forRender

    def generate(self, r, g, b, animal, maxHP = 50, initialHP = 50):
        self.maxHP = maxHP
        self.initialHP = initialHP
        self.color = (r, g, b, 1)

        gui = loader.loadModel("phase_3/models/gui/laff_o_meter.bam")
        if animal == "rabbit":
            animal = "bunny"
        headmodel = gui.find('**/' + animal + 'head')
        self.container['image'] = headmodel
        self.container['image_color'] = self.color
        self.setPos(0.16, 0, 0.155)
        self.resetFrameSize()
        self.setScale(0.08)
        self.frown = DirectFrame(parent=self.container, relief=None, image=gui.find('**/frown'))
        self.smile = DirectFrame(parent=self.container, relief=None, image=gui.find('**/smile'))
        self.eyes = DirectFrame(parent=self.container, relief=None, image=gui.find('**/eyes'))
        self.openSmile = DirectFrame(parent=self.container, relief=None, image=gui.find('**/open_smile'))
        self.tooth1 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_1'))
        self.tooth2 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_2'))
        self.tooth3 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_3'))
        self.tooth4 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_4'))
        self.tooth5 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_5'))
        self.tooth6 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_6'))

        self.teethList = [self.tooth6,
                        self.tooth5,
                        self.tooth4,
                        self.tooth3,
                        self.tooth2,
                        self.tooth1]
        if self.forRender:
            self.container['image_pos'] = (0, 0.01, 0)
            for tooth in self.teethList:
                tooth.setDepthWrite(False)
            self.eyes.setDepthWrite(False)
            self.smile.setDepthWrite(False)
            self.openSmile.setDepthWrite(False)
            self.frown.setDepthWrite(False)
        self.fractions = [0.0,
                        0.166666,
                        0.333333,
                        0.5,
                        0.666666,
                        0.833333]

        self.currentHealthLbl = DirectLabel(text=str(self.initialHP), parent=self.eyes, pos=(-0.425, 0, 0.05), scale=0.4, relief=None)
        self.maxHealthLbl = DirectLabel(text=str(self.maxHP), parent=self.eyes, pos=(0.425, 0, 0.05), scale=0.4, relief=None)
        if self.forRender:
            self.currentHealthLbl.setY(-0.01)
            self.maxHealthLbl.setY(-0.01)

        self.updateMeter(self.initialHP)
        gui.removeNode()
        return

    def start(self):
        taskMgr.add(self.updateMeterTask, "updateMeterTask")

    def updateMeterTask(self, task):
        if hasattr(base, 'localAvatar'):
            if str(base.localAvatar.getHealth()) != self.currentHealthLbl['text']:
                self.updateMeter(base.localAvatar.getHealth())
        else:
            return task.done
        return task.cont

    def updateMeter(self, health):
        self.adjustFace(health)

    def adjustFace(self, health):
        self.frown.hide()
        self.smile.hide()
        self.openSmile.hide()
        self.eyes.hide()
        for tooth in self.teethList:
            tooth.hide()
        if health <= 0:
            self.frown.show()
            self.container['image_color'] = self.deathColor
        elif health >= self.maxHP:
            self.smile.show()
            self.eyes.show()
            self.container['image_color'] = self.color
        else:
            self.openSmile.show()
            self.eyes.show()
            self.maxHealthLbl.show()
            self.currentHealthLbl.show()
            self.container['image_color'] = self.color
            self.adjustTeeth(health)
        self.animatedEffect(health - self.initialHP)
        self.adjustText(health)

    def animatedEffect(self, delta):
        if delta == 0:
            return
        name = 'effect'
        if delta > 0:
            ToontownIntervals.start(ToontownIntervals.getPulseLargerIval(self.container, name))
        else:
            ToontownIntervals.start(ToontownIntervals.getPulseSmallerIval(self.container, name))

    def adjustTeeth(self, health):
        for i in xrange(len(self.teethList)):
            if health > self.maxHP * self.fractions[i]:
                self.teethList[i].show()
            else:
                self.teethList[i].hide()

    def adjustText(self, health):
        if self.maxHealthLbl['text'] != str(self.maxHP) or self.currentHealthLbl['text'] != str(health):
            self.currentHealthLbl['text'] = str(health)

    def stop(self):
        taskMgr.remove("updateMeterTask")

    def disable(self):
        if not hasattr(self, 'frown'):
            notify.warning("Won't disable LaffOMeter, no var named frown.")
            return
        self.frown.destroy()
        self.smile.destroy()
        self.eyes.destroy()
        self.openSmile.destroy()
        self.tooth1.destroy()
        self.tooth2.destroy()
        self.tooth3.destroy()
        self.tooth4.destroy()
        self.tooth5.destroy()
        self.tooth6.destroy()
        del self.frown
        del self.smile
        del self.eyes
        del self.openSmile
        del self.tooth1
        del self.tooth2
        del self.tooth3
        del self.tooth4
        del self.tooth5
        del self.tooth6
        self.container["image"] = None
        return

    def delete(self):
        self.container.destroy()
        del self.container
        return

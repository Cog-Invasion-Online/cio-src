"""

  Filename: Char.py
  Created by: blach (??July14)

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.avatar import Avatar
from lib.coginvasion.nametag import NametagGlobals

from pandac.PandaModules import CharacterJointEffect, ModelNode

from direct.directnotify.DirectNotify import DirectNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

import random

notify = DirectNotify().newCategory("Char")

class Char(Avatar.Avatar):

    def __init__(self):
        try:
            self.Char_initialized
            return
        except:
            self.Char_initialized = 1
        Avatar.Avatar.__init__(self)
        self.avatarType = CIGlobals.CChar
        self.avatarName = None
        self.currentAnim = None
        self.charType = ""
        self.eyes = loader.loadTexture("phase_3/maps/eyes1.jpg", "phase_3/maps/eyes1_a.rgb")
        self.closedEyes = loader.loadTexture("phase_3/maps/mickey_eyes_closed.jpg", "phase_3/maps/mickey_eyes_closed_a.rgb")
        self.animFSM = ClassicFSM('Char', [State('off', self.enterOff, self.exitOff),
                                State('neutral', self.enterNeutral, self.exitNeutral),
                                State('walk', self.enterWalk, self.exitWalk),
                                State('run', self.enterRun, self.exitRun)], 'off', 'off')
        animStateList = self.animFSM.getStates()
        self.animFSM.enterInitialState()
        self.charId = -1

        Avatar.Avatar.initializeBodyCollisions(self, self.avatarType, 3.5, 1)

    def getNametagJoints(self):
        return []

    def stopAnimations(self):
        if hasattr(self, 'animFSM'):
            if not self.animFSM.isInternalStateInFlux():
                self.animFSM.request('off')
            else:
                notify.warning("animFSM in flux, state=%s, not requesting off" % self.animFSM.getCurrentState().getName())
        else:
            notify.warning("animFSM has been deleted")
        return

    def disable(self):
        self.stopBlink()
        self.stopAnimations()
        Avatar.Avatar.disable(self)
        return

    def delete(self):
        try:
            self.Char_deleted
        except:
            self.Char_deleted = 1
            del self.animFSM
            Avatar.Avatar.delete(self)

        return

    def setChat(self, chatString):
        if self.charType == CIGlobals.Mickey:
            self.dial = base.audio3d.loadSfx("phase_3/audio/dial/mickey.ogg")
        elif self.charType == CIGlobals.Minnie:
            self.dial = base.audio3d.loadSfx("phase_3/audio/dial/minnie.ogg")
        elif self.charType == CIGlobals.Goofy:
            self.dial = base.audio3d.loadSfx("phase_6/audio/dial/goofy.ogg")
        base.audio3d.attachSoundToObject(self.dial, self)
        self.dial.play()
        Avatar.Avatar.setChat(self, chatString)

    def setName(self, nameString, charName = None):
        self.avatarName = nameString
        Avatar.Avatar.setName(self, nameString, avatarType=self.avatarType, charName=charName)

    def setupNameTag(self, tempName = None):
        Avatar.Avatar.setupNameTag(self, tempName)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def generateChar(self, charType):
        self.charType = charType
        if charType == CIGlobals.Mickey or charType == CIGlobals.Minnie:
            self.loadModel("phase_3/models/char/" + charType.lower() + "-" + str(CIGlobals.ModelDetail(self.avatarType)) + ".bam")
            self.loadAnims({"neutral": "phase_3/models/char/" + charType.lower() + "-wait.bam",
                            "walk": "phase_3/models/char/" + charType.lower() + "-walk.bam",
                            "run": "phase_3/models/char/" + charType.lower() + "-run.bam",
                            "left-start": "phase_3.5/models/char/" + charType.lower() + "-left-start.bam",
                            "left": "phase_3.5/models/char/" + charType.lower() + "-left.bam",
                            "right-start": "phase_3.5/models/char/" + charType.lower() + "-right-start.bam",
                            "right": "phase_3.5/models/char/" + charType.lower() + "-right.bam"})
            if charType == CIGlobals.Mickey:
                self.mickeyEye = self.controlJoint(None, "modelRoot", "joint_pupilR")
                self.mickeyEye.setY(0.025)

            for bundle in self.getPartBundleDict().values():
                bundle = bundle['modelRoot'].getBundle()
                earNull = bundle.findChild('sphere3')
                if not earNull:
                    earNull = bundle.findChild('*sphere3')
                earNull.clearNetTransforms()

            for bundle in self.getPartBundleDict().values():
                charNodepath = bundle['modelRoot'].partBundleNP
                bundle = bundle['modelRoot'].getBundle()
                earNull = bundle.findChild('sphere3')
                if not earNull:
                    earNull = bundle.findChild('*sphere3')
                ears = charNodepath.find('**/sphere3')
                if ears.isEmpty():
                    ears = charNodepath.find('**/*sphere3')
                ears.clearEffect(CharacterJointEffect.getClassType())
                earRoot = charNodepath.attachNewNode('earRoot')
                earPitch = earRoot.attachNewNode('earPitch')
                earPitch.setP(40.0)
                ears.reparentTo(earPitch)
                earNull.addNetTransform(earRoot.node())
                ears.clearMat()
                ears.node().setPreserveTransform(ModelNode.PTNone)
                ears.setP(-40.0)
                ears.flattenMedium()
                ears.setBillboardAxis()

                self.startBlink()
        elif charType == CIGlobals.Pluto:
            self.loadModel("phase_6/models/char/pluto-1000.bam")
            self.loadAnims({"walk": "phase_6/models/char/pluto-walk.bam",
                                "neutral": "phase_6/models/char/pluto-neutral.bam",
                                "sit": "phase_6/models/char/pluto-sit.bam",
                                "stand": "phase_6/models/char/pluto-stand.bam"})

        elif charType == CIGlobals.Goofy:
            self.loadModel("phase_6/models/char/TT_G-1500.bam")
            self.loadAnims({"neutral": "phase_6/models/char/TT_GWait.bam",
                                "walk": "phase_6/models/char/TT_GWalk.bam"})
        else:
            raise StandardError("unknown char %s!" % (charType))
        #self.getGeomNode().setScale(1.25)
        Avatar.Avatar.initShadow(self)

    def initializeLocalCollisions(self, name, radius):
        Avatar.Avatar.initializeLocalCollisions(self, radius, 2, name)

    def startBlink(self):
        randomStart = random.uniform(0.5, 5)
        taskMgr.add(self.blinkTask, "blinkTask")

    def stopBlink(self):
        taskMgr.remove("blinkTask")
        taskMgr.remove("doBlink")
        taskMgr.remove("openEyes")

    def blinkTask(self, task):
        taskMgr.add(self.doBlink, "doBlink")
        delay = random.uniform(0.5, 7)
        task.delayTime = delay
        return task.again

    def doBlink(self, task):
        self.closeEyes()
        taskMgr.doMethodLater(0.2, self.openEyes, "openEyes")
        return task.done

    def closeEyes(self):
        self.find('**/joint_pupilR').hide()
        self.find('**/joint_pupilL').hide()
        if self.charType == CIGlobals.Mickey:
            self.mickeyEye.setY(-0.025)
            self.mickeyEye.hide()

        self.find('**/eyes').setTexture(self.closedEyes, 1)

    def openEyes(self, task):
        self.find('**/joint_pupilR').show()
        self.find('**/joint_pupilL').show()
        if self.charType == CIGlobals.Mickey:
            self.mickeyEye.setY(0.025)
            self.mickeyEye.show()

        self.find('**/eyes').setTexture(self.eyes, 1)
        return task.done

    def enterOff(self):
        self.currentAnim = None
        return

    def exitOff(self):
        pass

    def enterNeutral(self):
        self.loop("neutral")

    def exitNeutral(self):
        self.stop()

    def enterWalk(self):
        self.loop("walk")

    def exitWalk(self):
        self.stop()

    def enterRun(self):
        self.loop("run")

    def exitRun(self):
        self.stop()

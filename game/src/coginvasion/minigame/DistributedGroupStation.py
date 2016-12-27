# Filename: DistributedGroupStation.py
# Created by:  blach (06Jun15)

from pandac.PandaModules import CollisionSphere, CollisionNode
from direct.distributed.DistributedObject import DistributedObject
from direct.gui.DirectGui import DirectButton
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, LerpPosInterval, LerpQuatInterval, Sequence, Func

from src.coginvasion.globals import CIGlobals
from src.coginvasion.npc.NPCWalker import NPCWalkInterval, NPCLookInterval
import GroupStation

class DistributedGroupStation(GroupStation.GroupStation, DistributedObject):
    notify = directNotify.newCategory("DistributedGroupStation")
    numPlayers2SphereRadius = {3: 13, 4: 12, 8: 13.5}
    numPlayers2SphereSx = {3: 1.0, 4: 1.15, 8: 1.15}
    numPlayers2SphereSy = {3: 1.0, 4: 0.8, 8: 1.0}
    numPlayers2SphereY = {3: 0.0, 4: 5.0, 8: 5.0}
    numPlayers2CamPos = {3: (0, 30.0, 22.5), 4: (0, 30.0, 22.5), 8: (0, 35.0, 22.5)}

    def __init__(self, cr):
        try:
            self.DistributedGroupStation_initialized
            return
        except:
            self.DistributedGroupStation_initialized = 1
        DistributedObject.__init__(self, cr)
        self.abortBtn = None
        self._name = None
        self.mySlot = None
        self.camIval = None
        return

    def __initCollisions(self, name):
        self.notify.debug("Initializing collision sphere...")
        numSlots = len(self.circles)
        ss = CollisionSphere(0,0,0,self.numPlayers2SphereRadius[numSlots])
        ss.setTangible(0)
        snode = CollisionNode(name)
        snode.add_solid(ss)
        snode.set_collide_mask(CIGlobals.WallBitmask)
        self.snp = self.attach_new_node(snode)
        self.snp.setZ(3)
        self.snp.setY(self.numPlayers2SphereY[numSlots])
        self.snp.setSx(self.numPlayers2SphereSx[numSlots])
        self.snp.setSy(self.numPlayers2SphereSy[numSlots])
        self.acceptOnce("enter" + self.snp.node().getName(), self.__handleEnterCollisionSphere)

    def __deleteCollisions(self):
        self.ignore("enter" + self.snp.node().getName())
        self.snp.removeNode()
        del self.snp

    def __handleEnterCollisionSphere(self, entry):
        self.notify.debug("Entering collision sphere...")
        self.d_requestEnter()

    def setTimerTime(self, time):
        GroupStation.GroupStation.setTimerTime(self, time)

    def setLocationPoint(self, lp):
        GroupStation.GroupStation.setLocationPoint(self, lp)

    def avatarEnter(self, slot, avId, x, y):
        toon = self.cr.doId2do.get(avId)
        if toon:

            toon.stopSmooth()

            def doTurn():
                turn = Sequence(NPCLookInterval(toon, self.sign, fluid = 1, durationFactor = 0.0035), Func(toon.loop, 'neutral'))
                turn.start()
            
            circle2Run2 = self.circles[slot - 1]

            if avId == base.localAvatar.doId:
                self.mySlot = slot

                localAvatar.stopSmartCamera()
                
                oPos = camera.getPos(render)
                oHpr = camera.getHpr(render)

                localAvatar.detachCamera()

                camPos = self.numPlayers2CamPos[len(self.circles)]
                camera.setPos(self, camPos)
                camPos = camera.getPos(render)
                
                camera.lookAt(self)
                camHpr = camera.getHpr()

                self.camIval = Sequence(Parallel(
                    LerpPosInterval(
                        camera,
                        duration = 1.5,
                        pos = camPos,
                        startPos = oPos,
                        blendType = 'easeOut'
                    ),
                    LerpQuatInterval(
                        camera,
                        duration = 1.5,
                        hpr = camHpr,
                        startHpr = oHpr,
                        blendType = 'easeOut'
                    )
                ), Func(self.createStationAbortGui)); self.camIval.start()

            runTrack = Sequence(Func(toon.loop, 'run'), NPCWalkInterval(toon,
                circle2Run2.getPos(render), 0.1, startPos=(x, y, toon.getZ())), Func(doTurn))
            runTrack.start()

            #self.cr.playGame.getPlace().fsm.request('station')

    def avatarExit(self, avId):
        toon = self.cr.doId2do.get(avId)
        if toon:
            toon.startSmooth()
            if avId == localAvatar.doId:
                self.exitMinigameStationSlot()

    def exitMinigameStationSlot(self):
        self.acceptOnce("enter" + self.snp.node().getName(), self.__handleEnterCollisionSphere)
        self.cr.playGame.getPlace().fsm.request('walk')

    def createStationAbortGui(self):
        qt_btn = loader.loadModel("phase_3/models/gui/quit_button.bam")
        self.abortBtn = CIGlobals.getExitButton(cmd = self.d_requestAbort, pos = (0, 0, 0.85))

    def deleteStationAbortGui(self):
        if hasattr(self, 'abortBtn') and self.abortBtn:
            self.abortBtn.destroy()
            self.abortBtn = None

    def d_requestEnter(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate("requestEnter", [base.localAvatar.getX(render), base.localAvatar.getY(render)])

    def d_requestAbort(self):
        self.deleteStationAbortGui()
        self.sendUpdate("requestAbort", [self.mySlot])

    def abort(self):
        self.exitMinigameStationSlot()

    def d_leaving(self):
        self.sendUpdate("leaving", [])

    def fullStation(self):
        self.cr.playGame.getPlace().fsm.request('walk')

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.reparentTo(render)
        self._name = self.uniqueName("MinigameStation")
        self.__initCollisions(self._name)

    def disable(self):
        DistributedObject.disable(self)
        self.detachNode()

    def delete(self):
        DistributedObject.delete(self)
        self.__deleteCollisions()
        GroupStation.GroupStation.delete(self)
        self.tb = None
        self.abortBtn = None
        self._name = None
        self.mySlot = None
        return

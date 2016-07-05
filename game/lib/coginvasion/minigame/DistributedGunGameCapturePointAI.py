########################################
# Filename: DistributedGunGameCapturePointAI.py
# Created by: DecodedLogic (17Apr16)
########################################

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.task.Task import Task

from lib.coginvasion.minigame import GunGameGlobals as GGG

class CaptureState:
    IDLE, IN_PROGRESS, CAPTURED, RESETTING = range(4)

class DistributedGunGameCapturePointAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedGunGameCapturePointAI')

    # Reset the capture point if captured and without someone
    # standing on it after this amount of seconds.
    EMPTY_RESET_TIME = 4.5

    # The time it takes for the animation on the client side to complete.
    # At the end, this will stop the capture.
    REVERSE_CAPTURE_TIME = 1.5

    # The time it takes for the animation on the client side to complete.
    # At the end, this will capture the point.
    # Originally, 8.0, but for now will be 0.0, once you're alone you cap.
    CAPTURE_TIME = 0.0

    # The time it takes for the animation on the client side to complete.
    # At the end, this will return the point to default.
    # Originally 10.75, now 0.0.
    RESET_TIME = 0.0
    
    # How many points the king gets per second.
    POINTS_AS_KING = 2

    # How Capturing Works
    # Because 0 is used to reset the capture point and 0 is the id of red,
    # you must add 2 to the teamId to set that a team has captured the point.
    # You set the capture to 1, if it's a free-for-all capture.

    def __init__(self, air, mg):
        DistributedNodeAI.__init__(self, air)
        self.mg = mg
        self.team = -2
        self.resetTaskName = None
        self.captureAttemptTaskName = None
        self.awardKingTaskName = None
        self.elapsedCaptureTime = 0
        self.elapsedCaptureResetTime = 0
        self.state = CaptureState.IDLE
        self.resetCaptureTime = self.RESET_TIME

        # The one who has captured this point.
        # For free-for-all KOTH.
        self.king = None
        self.kingId = None
        self.kingOnPoint = False

        # The Toon that is trying to capture the point.
        self.primaryContester = None

        # Toons who contesting the capture.
        self.contesters = []

    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)
        self.resetTaskName = self.uniqueName('ResetPoint')
        self.captureAttemptTaskName = self.uniqueName('CaptureAttempt')
        self.awardKingTaskName = self.uniqueName('AwardKing')

    def delete(self):
        # We need to clean up to prevent memory leaks.
        taskMgr.removeTasksMatching(self.captureAttemptTaskName)
        taskMgr.removeTasksMatching(self.resetTaskName)
        taskMgr.removeTasksMatching(self.awardKingTaskName)
        self.contesters = []
        self.resetHill()
        self.d_startCircleAnim(3)
        del self.king
        del self.kingId
        del self.kingOnPoint
        del self.primaryContester
        del self.contesters
        del self.team
        del self.mg
        del self.resetTaskName
        del self.elapsedCaptureTime
        del self.captureAttemptTaskName
        del self.elapsedCaptureResetTime
        del self.state
        del self.resetCaptureTime
        self.removeNode()
        DistributedNodeAI.delete(self)

    def setKing(self, avId):
        if avId:
            avatar = self.air.doId2do.get(avId)

            if not self.king:
                self.king = avatar
                self.kingId = avId
                self.mg.d_setKOTHKing(avId)
        else:
            self.king = None
            self.kingId = None
            self.mg.d_setKOTHKing(0)

    def getKing(self):
        return self.king

    def getKingId(self):
        return self.kingId

    def __handleCapture(self, task):
        self.elapsedCaptureTime += task.time
        if self.elapsedCaptureTime >= self.CAPTURE_TIME:
            if self.primaryContester:
                self.setKing(self.primaryContester.doId)
                self.b_setCaptured(1)
                self.kingOnPoint = True
                self.state = CaptureState.CAPTURED
                self.sendUpdate('updateStatus', [1, self.primaryContester.doId])
            return Task.done
        return Task.again
    
    def __handleAward(self, task):
        if hasattr(self, 'mg'):
            points = self.mg.getKOTHPoints(self.kingId)
            if points < 100 and self.kingId:
                self.mg.b_setKOTHPoints(self.kingId, points + self.POINTS_AS_KING)
                return Task.again
            elif points >= 100:
                self.mg.sendUpdate('teamWon', [0])
        return Task.done

    def resetHill(self):
        self.b_setCaptured(0)
        self.setKing(None)
        self.kingOnPoint = False
        self.primaryContester = None
        self.state = CaptureState.IDLE
        self.sendUpdate('updateStatus', [2, 0])
        self.elapsedCaptureResetTime = 0
        self.elapsedCaptureTime = 0
        if len(self.contesters) == 1 and not self.primaryContester:
            # The primary contester is gone and nobody else is contesting,
            # let's have the last remaining contester start capturing!
            self.beginCapture(self.air.doId2do.get(self.contesters[0]))

    def __handleCaptorExit(self, task):
        self.resetHill()
        
        if len(self.contesters) == 1:
            # The primary contester is gone and nobody else is contesting,
            # let's have the last remaining contester start capturing!
            self.beginCapture(self.air.doId2do.get(self.contesters[0]))
        return Task.done

    def __handleKingExit(self, task):
        self.elapsedCaptureResetTime += task.time
        if self.elapsedCaptureResetTime >= self.resetCaptureTime:
            self.resetHill()
            return Task.done
        return Task.again

    def d_startCircleAnim(self, direction):
        if direction == 1:
            self.elapsedCaptureResetTime = 0
            self.elapsedCaptureTime = 0
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startCircleAnim', [direction, timestamp])

    def beginCapture(self, captor):
        self.primaryContester = captor
        self.resetCaptureTime = self.RESET_TIME
        self.elapsedCaptureTime = 0
        #self.d_startCircleAnim(0)
        taskMgr.add(self.__handleCapture, self.captureAttemptTaskName)
        self.state = CaptureState.IN_PROGRESS

    # The avatar has jumped onto the point and is
    # attempting to capture it.
    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)

        # Dead avatars cannot enter the point.
        # Ignore any apparent entrances from them.
        if avatar and avatar.isDead() or not hasattr(self, 'mg'):
            return

        if not avatar:
            if avId in self.contesters:
                self.contesters.remove(avId)
            elif avId == self.kingId:
                # A disconnected avatar is the king, let's reset the point.
                self.resetHill()
            return

        if not avId in self.contesters:
            if self.king and self.king.doId == avatar.doId:
                # LEBRON JAMES HAS RETURNED TO CLEVELAND!!
                # (The king has returned to the point.)
                taskMgr.removeTasksMatching(self.resetTaskName)
                self.d_startCircleAnim(3)
                self.kingOnPoint = True
                self.state = CaptureState.CAPTURED
                
                if len(taskMgr.getTasksNamed(self.awardKingTaskName)) == 0:
                    taskMgr.doMethodLater(1, self.__handleAward, self.awardKingTaskName)
            elif self.primaryContester and self.primaryContester.doId == avatar.doId:
                # The primary contester has returned to the point and there's no longer any
                # others contesting his capture.
                if len(self.contesters) == 0 and self.state == CaptureState.RESETTING:
                    self.sendUpdate('handleContesters', [0])
                    self.sendUpdate('updateStatus', [0, avId])
                    taskMgr.removeTasksMatching(self.resetTaskName)
                    self.beginCapture(avatar)
            else:
                if len(self.contesters) == 0 and not self.primaryContester:
                    # Let's begin capturing this point.
                    self.beginCapture(avatar)
                    self.sendUpdate('updateStatus', [0, avId])
                elif self.primaryContester and self.primaryContester.doId != avatar.doId:
                    # CONTEST the capture.
                    self.contesters.append(avId)

                    if self.state == CaptureState.RESETTING and self.king:
                        # We need to lower the time it takes to reset now.
                        self.resetCaptureTime = self.resetCaptureTime - 0.5
                    elif self.state == CaptureState.IDLE and not self.king:
                        # The avatar is no longer able to capture.
                        taskMgr.removeTasksMatching(self.captureAttemptTaskName)
                    elif self.state == CaptureState.CAPTURED and self.king:
                        # The avatar is trying to capture before the old avatar actually left.
                        #self.resetCaptureTime = self.resetCaptureTime - 0.5
                        #self.d_startCircleAnim(1)
                        taskMgr.add(self.__handleKingExit, self.resetTaskName)
                        taskMgr.removeTasksMatching(self.awardKingTaskName)
                        self.state = CaptureState.RESETTING

                    if not self.kingOnPoint:
                        self.sendUpdate('handleContesters', [1])
                        if self.state == CaptureState.IN_PROGRESS:
                            # We need to pause the capture.
                            taskMgr.removeTasksMatching(self.captureAttemptTaskName)

    # The avatar has died or hopped off the point.
    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        
        if not hasattr(self, 'mg'): return

        if avId in self.contesters and avatar != self.king:
            self.contesters.remove(avId)

            if len(self.contesters) == 0 and self.primaryContester and not self.state == CaptureState.CAPTURED:
                # There's no longer any more contesters on the point.
                self.sendUpdate('handleContesters', [0])
                taskMgr.add(self.__handleCapture, self.captureAttemptTaskName)
                self.state = CaptureState.IN_PROGRESS
            elif len(self.contesters) == 1 and not self.primaryContester or len(self.contesters) == 1 and self.state == CaptureState.RESETTING:
                # The primary contester is gone and nobody else is contesting,
                # let's have the last remaining contester start capturing!
                self.beginCapture(self.air.doId2do.get(self.contesters[0]))
            elif len(self.contesters) == 0 and self.king and self.state == CaptureState.CAPTURED:
                if len(taskMgr.getTasksNamed(self.awardKingTaskName)) == 0:
                    taskMgr.doMethodLater(1, self.__handleAward, self.awardKingTaskName)
        elif self.primaryContester and avatar and self.primaryContester.doId == avatar.doId or self.primaryContester and self.primaryContester == self.king or self.primaryContester and not avatar:
            self.kingOnPoint = False
            if self.state == CaptureState.IN_PROGRESS:
                # The primary contester is stepping off the point while attempting to capture.
                # Begin reversing the capture.
                taskMgr.removeTasksMatching(self.captureAttemptTaskName)
                self.d_startCircleAnim(2)
                taskMgr.doMethodLater(self.REVERSE_CAPTURE_TIME, self.__handleCaptorExit, self.resetTaskName)
                self.state = CaptureState.RESETTING
            elif self.state == CaptureState.CAPTURED:
                # The primary contester has stepped off the captured point.
                # Begin resetting it.
                #self.d_startCircleAnim(1)
                taskMgr.add(self.__handleKingExit, self.resetTaskName)
                taskMgr.removeTasksMatching(self.awardKingTaskName)
                self.state = CaptureState.RESETTING


    def b_setCaptured(self, teamId):
        self.setCaptured(teamId)
        self.sendUpdate('setCaptured', [teamId])

    def setCaptured(self, teamId):
        if (teamId - 2) in GGG.TeamNameById.values():
            self.team = (teamId - 2)
        if len(taskMgr.getTasksNamed(self.awardKingTaskName)) == 0:
            taskMgr.doMethodLater(1, self.__handleAward, self.awardKingTaskName)

    def getCaptured(self):
        if self.team < 0:
            return self.team + 2
        return self.team

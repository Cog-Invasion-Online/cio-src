"""

  Filename: DistributedRaceGameAI.py
  Created by: blach (07Oct14)

"""

from src.coginvasion.globals import CIGlobals
import DistributedMinigameAI

class DistributedRaceGameAI(DistributedMinigameAI.DistributedMinigameAI):

    def __init__(self, cr):
        try:
            self.DistributedRaceGameAI_initialized
            return
        except:
            self.DistributedRaceGameAI_initialized = 1
        DistributedMinigameAI.DistributedMinigameAI.__init__(self, cr)
        self.cr = cr
        self.game = CIGlobals.RaceGame
        self.winnerY = 203.00
        self.winnerPrize = 100
        self.loserPrize = 5
        return

    def monitorAvatarPositions(self, task):
        for avatar in self.avatars:
            if not avatar.isEmpty():
                if self.hasPassedFinishLine(avatar):
                    self.d_gameOver(winner=1, winnerDoId=[avatar.doId])
                    return task.done
        return task.cont

    def hasPassedFinishLine(self, avatar):
        return (avatar.getY(render) >= self.winnerY)

    def requestToonLane(self):
        """ This is called by the client so the AI can figure out
        which lane the client's avatar should stand in. """
        doId = self.air.getAvatarIdFromSender()
        for avatar in self.avatars:
            if avatar.doId == doId:
                lane = self.avatars.index(avatar)
                self.d_setToonLane(lane, doId)

    def d_setToonLane(self, lane, doId):
        self.sendUpdateToAvatarId(doId, 'setToonLane', [lane])

    def announceGenerate(self):
        DistributedMinigameAI.DistributedMinigameAI.announceGenerate(self)
        taskMgr.add(self.monitorAvatarPositions, self.cr.uniqueName("monitorAvatarPositions"))

    def delete(self):
        try:
            self.DistributedRaceGameAI_deleted
            return
        except:
            self.DistributedRaceGameAI_deleted = 1
        DistributedMinigameAI.DistributedMinigameAI.delete(self)
        taskMgr.remove(self.cr.uniqueName("monitorAvatarPositions"))

# Filename: DistributedNPCToon.py
# Created by:  blach (31Jul15)

from panda3d.core import CollisionNode, CollisionSphere
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, LerpPosInterval, LerpQuatInterval, Sequence, Wait, Func

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quests import Quests
from lib.coginvasion.nametag import NametagGlobals
from DistributedToon import DistributedToon

class DistributedNPCToon(DistributedToon):
    notify = directNotify.newCategory("DistributedNPCToon")

    def __init__(self, cr):
        DistributedToon.__init__(self, cr)
        self.collisionNodePath = None
        self.cameraTrack = None
        self.originIndex = None
        self.npcId = None
        self.currentChatIndex = 0
        self.chatArray = None

    def setLoadout(self, foo):
        pass

    def lookAtAvatar(self, avId):
        av = self.cr.doId2do.get(avId)
        if av:
            self.headsUp(av)

    def setNpcId(self, id):
        self.npcId = id

    def getNpcId(self):
        return self.npcId

    def setOriginIndex(self, index):
        self.originIndex = index

    def getOriginIndex(self):
        return self.originIndex

    def __setupCollisions(self):
        sphere = CollisionSphere(0, 0, 0, 4)
        sphere.setTangible(0)
        collisionNode = CollisionNode(self.uniqueName('NPCToonSphere'))
        collisionNode.addSolid(sphere)
        collisionNode.setCollideMask(CIGlobals.WallBitmask)
        self.collisionNodePath = self.attachNewNode(collisionNode)
        self.collisionNodePath.setY(1.5)

    def __removeCollisions(self):
        if self.collisionNodePath:
            self.collisionNodePath.removeNode()
            self.collisionNodePath = None

    def handleEnterCollision(self, entry):
        self.cr.playGame.getPlace().fsm.request('stop')
        base.localAvatar.stopSmartCamera()
        self.sendUpdate('requestEnter', [])

    def doCameraNPCInteraction(self):
        currCamPos = camera.getPos()
        currCamHpr = camera.getHpr()
        camera.setX(camera.getX() + 5)
        camera.setY(camera.getY() + 5)
        camera.headsUp(self)
        newCamPos = camera.getPos()
        newCamHpr = camera.getHpr()
        camera.setPos(currCamPos)
        camera.setHpr(currCamHpr)

        self.cameraTrack = Parallel(
            LerpPosInterval(camera, duration = 1.0, pos = newCamPos, startPos = currCamPos, blendType = 'easeOut'),
            LerpQuatInterval(camera, duration = 1.0, quat = newCamHpr, startHpr = currCamHpr, blendType = 'easeOut')
        )
        self.cameraTrack.start()

    def stopCameraTrack(self):
        if self.cameraTrack:
            self.cameraTrack.finish()
            self.cameraTrack = None

    def oneChatThenExit(self):
        self.acceptOnce('mouse1-up', self.d_requestExit)

    def enterAccepted(self):
        self.doCameraNPCInteraction()
        questData = base.localAvatar.questManager.getQuestAndIdWhereCurrentObjectiveIsToVisit(self.npcId)
        if questData:
            quest = questData[1]
            self.currentQuestObjective = quest.currentObjectiveIndex
            self.currentQuestId = questData[0]
            self.currentChatIndex = 0
            if CIGlobals.NPCToonDict[self.npcId][3] == CIGlobals.NPC_HQ:
                if not quest.isComplete():
                    self.doNPCChat(array = Quests.QuestHQOfficerDialogue)
            if CIGlobals.NPCToonDict[self.npcId][3] == CIGlobals.NPC_REGULAR:
                self.doNPCChat(array = Quests.QuestNPCDialogue)

    def doNPCChat(self, array = Quests.QuestNPCDialogue, chat = None):
        if array and not chat:
            self.chatArray = array
            self.b_setChat(array[self.currentQuestId][self.currentQuestObjective][self.currentChatIndex])
            self.currentChatIndex += 1
            Sequence(Wait(0.1), Func(self.acceptOnce, 'mouse1-up', self.doNextNPCChat)).start()
        elif chat and not array:
            self.b_setChat(chat)
            Sequence(Wait(0.1), Func(self.acceptOnce, 'mouse1-up', self.d_requestExit)).start()

    def d_requestExit(self):
        self.sendUpdate('requestExit', [])

    def doNextNPCChat(self):
        if self.currentChatIndex >= len(self.chatArray[self.currentQuestId][self.currentQuestObjective]):
            self.chatArray = None
            self.d_requestExit()
        else:
            self.doNPCChat(self.chatArray)

    def rejectEnter(self):
        self.exitAccepted()

    def exitAccepted(self):
        self.stopCameraTrack()
        self.cr.playGame.getPlace().fsm.request('walk')
        self.acceptCollisions()

    def acceptCollisions(self):
        self.acceptOnce('enter' + self.uniqueName('NPCToonSphere'), self.handleEnterCollision)

    def ignoreCollisions(self):
        self.ignore('enter' + self.uniqueName('NPCToonSphere'))

    def __npcOriginPoll(self, task):
        if task.time > 4.0:
            self.notify.warning("Giving up waiting for npc origin after %d seconds. Will parent to render." % task.time)
            self.reparentTo(render)
            return task.done
        npcOrigin = render.find('**/npc_origin_' + str(self.originIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            return task.done
        return task.cont

    def startNPCOriginPoll(self):
        base.taskMgr.add(self.__npcOriginPoll, self.uniqueName('NPCOriginPoll'))

    def stopNPCOriginPoll(self):
        base.taskMgr.remove(self.uniqueName('NPCOriginPoll'))

    def setupNameTag(self, tempName = None):
        DistributedToon.setupNameTag(self, tempName)
        self.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.nametag.setActive(0)
        self.nametag.updateAll()

    def announceGenerate(self):
        DistributedToon.announceGenerate(self)
        self.startLookAround()
        self.__setupCollisions()
        npcOrigin = render.find('**/npc_origin_' + str(self.originIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
        else:
            self.startNPCOriginPoll()
        self.acceptCollisions()

    def disable(self):
        self.ignore('mouse1-up')
        self.stopLookAround()
        self.stopNPCOriginPoll()
        self.chatArray = None
        self.originIndex = None
        self.npcId = None
        self.stopCameraTrack()
        self.ignoreCollisions()
        self.__removeCollisions()
        DistributedToon.disable(self)

# Filename: DistributedDisneyCharAI.py
# Created by:  blach (21Jun16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.distributed.ClockDelta import globalClockDelta

from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI

from DisneyCharGlobals import *

import random

class DistributedDisneyCharAI(DistributedAvatarAI, DistributedSmoothNodeAI):
    notify = directNotify.newCategory('DistributedDisneyCharAI')

    def __init__(self, air, charId):
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        self.fsm = ClassicFSM('DDCharAI',
                              [State('off', self.enterOff, self.exitOff),
                               State('neutral', self.enterNeutral, self.exitNeutral),
                               State('walking', self.enterWalking, self.exitWalking)],
                              'off', 'off')
        self.fsm.enterInitialState()
        self.charId = charId
        self.avatars = []
        self.inConvo = False
        self.chatsThisConvo = 0
        self.toonOfInterest = 0
        self.saidGoodbye = False
        self.currentPointLetter = None
        self.lastPointLetter = None
        self.talkEnabled = True

    def requestStateData(self):
        if self.charId == SAILOR_DONALD:
            return

        avId = self.air.getAvatarIdFromSender()
        if self.fsm.getCurrentState().getName() == 'neutral':
            self.sendUpdateToAvatarId(avId, 'doNeutral', [self.currentPointLetter])
        elif self.fsm.getCurrentState().getName() == 'walking':
            self.sendUpdateToAvatarId(avId, 'doWalking', [self.currentPointLetter, self.lastPointLetter, self.walkingTimestamp])

    def getCharId(self):
        return self.charId

    def chooseChat(self, chatType):
        if chatType == 'greet':
            sharedOrMine = random.choice([SHARED_GREETINGS, CHAR_GREETINGS])

        elif chatType == 'comment':
            num = random.randint(1, 100)
            if num in SHARED_COMMENT_CHANCE:
                sharedOrMine = SHARED_COMMENTS
            elif num in UNIQUE_COMMENT_CHANCE:
                sharedOrMine = CHAR_COMMENTS

        elif chatType == 'bye':
            sharedOrMine = random.choice([SHARED_GOODBYES, CHAR_GOODBYES])

        if sharedOrMine < CHAR_GREETINGS:
            # It's shared
            chatList = CHATTER[sharedOrMine]
        elif sharedOrMine >= CHAR_GREETINGS:
            # It's unique
            chatList = CHATTER[sharedOrMine][self.charId]

        chat = random.choice(chatList)
        index = chatList.index(chat)
        return [sharedOrMine, index]

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterNeutral(self, pickRandomPoint = False):
        if self.talkEnabled:
            taskMgr.doMethodLater(random.uniform(*CHECK_FOR_PEEPS_RANGE), self.__neutralTask, self.uniqueName('neutralTask'))
        if self.charId != SAILOR_DONALD:
            self.startLonelyTask()
            if pickRandomPoint:
                self.currentPointLetter = random.choice(WALK_POINTS[self.charId].keys())
            self.sendUpdate('doNeutral', [self.currentPointLetter])

    def startLonelyTask(self):
        self.lonelyThreshold = random.randint(*TIMES_LONELY_RANGE)
        self.timesLonely = 0
        taskMgr.doMethodLater(random.uniform(*LONELY_TIME_RANGE), self.__lonelyTask, self.uniqueName('lonelyTask'))

    def __lonelyTask(self, task):
        # Nobody came over to talk to me.
        if self.isLonely() and not self.inConvo:
            self.timesLonely += 1
            if self.timesLonely >= self.lonelyThreshold:
                # Let's walk somewhere else -- maybe we'll find people there.
                self.fsm.request('walking')
                return task.done

        task.delayTime = random.uniform(*TIMES_LONELY_RANGE)
        return task.again

    def __neutralTask(self, task):
        if self.saidGoodbye:
            # Alright, let's go walking.
            self.fsm.request('walking')
            return task.done

        # Wait for peoples to walk over to me!
        if self.wantsToChat() and not self.inConvo:
            # Aye! We got someone!
            taskMgr.remove(self.uniqueName('lonelyTask'))
            # Let's pick a random person out of my huge circle of friends to talk to.
            peep = random.choice(self.avatars)
            self.toonOfInterest = peep
            # Let's greet them!
            chatType, index = self.chooseChat('greet')
            self.chatsThisConvo = 1
            # Alright, tell all of the DisneyChar clients to talk to this person!
            self.sendUpdate('talk2Toon', [chatType, index, peep])
            # Don't mess with me, i'm in a conversation!
            self.inConvo = True
            task.delayTime = random.uniform(*TALK_AGAIN_RANGE)
            return task.again
        elif self.inConvo:
            # Seems like they're still interested in me. Let's keep talking.
            if not self.toonOfInterest in self.avatars:
                # Wait, no they're not.
                if self.wantsToChat():
                    # Luckily I have more friends to talk to!
                    self.toonOfInterest = random.choice(self.avatars)
                elif self.isLonely():
                    # Wow, all my friends left me.
                    self.startLonelyTask()
                    self.inConvo = False
                    task.delayTime = random.uniform(*CHECK_FOR_PEEPS_RANGE)
                    return task.again

            if self.chatsThisConvo >= CHAT_THRESHOLD:
                # Ugh, i'm bored. Say goodbye and go for a walk.
                chatType, index = self.chooseChat('bye')
                self.sendUpdate('talk2Toon', [chatType, index, self.toonOfInterest])
                self.saidGoodbye = True
                task.delayTime = 3.0
                return task.again

            self.toonOfInterest = random.choice(self.avatars)

            # Say a random comment.
            chatType, index = self.chooseChat('comment')
            self.sendUpdate('talk2Toon', [chatType, index, self.toonOfInterest])
            self.chatsThisConvo += 1
            task.delayTime = random.uniform(*TALK_AGAIN_RANGE)
            return task.again

        task.delayTime = random.uniform(*CHECK_FOR_PEEPS_RANGE)
        return task.again

    def exitNeutral(self):
        taskMgr.remove(self.uniqueName('lonelyTask'))
        taskMgr.remove(self.uniqueName('neutralTask'))
        self.chatsThisConvo = 0
        self.toonOfInterest = 0
        self.saidGoodbye = False
        self.inConvo = False
        del self.lonelyThreshold
        del self.timesLonely

    def enterWalking(self):
        if self.currentPointLetter is None:
            # We haven't walked anywhere yet.
            # Choose any random point.
            point = random.choice(WALK_POINTS[self.charId].items())
            pointLetter = point[0]
            timeUntilNeutral = 1.0
        else:
            pointLetter = self.choosePoint()
            point = WALK_POINTS[self.charId][pointLetter][0]
            lastPoint = WALK_POINTS[self.charId][self.currentPointLetter][0]

            timeUntilNeutral = (point.getXy() - lastPoint.getXy()).length() * 0.2

            if self.charId == PLUTO:
                timeUntilNeutral += PLUTO_STANDUP_TIME
            elif self.charId == SLEEP_DONALD:
                timeUntilNeutral += SLEEP_DONALD_N2W_TIME

        taskMgr.doMethodLater(timeUntilNeutral, self.__walkingTask, self.uniqueName('walkingTask'))
        self.walkingTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('doWalking', [pointLetter, self.currentPointLetter, self.walkingTimestamp])
        self.lastPointLetter = self.currentPointLetter
        self.currentPointLetter = pointLetter

    def __walkingTask(self, task):
        self.fsm.request('neutral')
        return task.done

    def exitWalking(self):
        taskMgr.remove(self.uniqueName('walkingTask'))

    def choosePoint(self):
        accessiblePointIndices = WALK_POINTS[self.charId][self.currentPointLetter][1]
        return random.choice(accessiblePointIndices)

    def isLonely(self):
        return len(self.avatars) == 0

    def wantsToChat(self):
        return (self.fsm.getCurrentState().getName() == 'neutral' and len(self.avatars) > 0)

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if not avId in self.avatars:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.acceptOnce(toon.getDeleteEvent(), self.avatarExit)
                self.acceptOnce(toon.getZoneChangeEvent(), self.avatarExit, [avId])
                self.avatars.append(avId)

    def avatarExit(self, avId = None, foo = None, foo2 = None):
        if avId == None:
            avId = self.air.getAvatarIdFromSender()
        if avId in self.avatars:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.ignore(toon.getZoneChangeEvent())
                self.ignore(toon.getDeleteEvent())
            self.avatars.remove(avId)

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        data = CHAR_DATA[self.charId]
        self.talkEnabled = data[4]
        self.fsm.request('neutral', [True])

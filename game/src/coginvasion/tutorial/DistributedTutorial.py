# Filename: DistributedTutorial.py
# Created by:  blach (16Oct15)

from pandac.PandaModules import NodePath, CompassEffect

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, LerpQuatInterval, LerpPosInterval, LerpHprInterval

from src.coginvasion.toon.Toon import Toon
from src.coginvasion.npc import NPCGlobals
from libpandadna import *
from src.coginvasion.hood.SkyUtil import SkyUtil
from src.coginvasion.gui.WhisperPopup import WhisperPopup
from src.coginvasion.globals import CIGlobals, ChatGlobals
from src.coginvasion.nametag import NametagGlobals

class DistributedTutorial(DistributedObject):
    notify = directNotify.newCategory('DistributedTutorial')

    GUIDE_NAME = 'Professor Prepostera'
    GUIDE_START_POS = (5, 10, -0.5)
    GUIDE_WATCH_POS = (12.4, 27.92, 0)
    GUIDE_WATCH_HPR = (41.63, 0, 0)
    GUIDE_INTRO_SPEECH = ['Hey, looks like you made it!', 'So, welcome to OToontown.',
     'OToontown is short for Old Toontown, or Toontown from the past.',
     'Not long ago, Toons used to live in present day Toontown.',
     'Unfortunately, the Cogs planned a mega-invasion that was sure to be a complete takeover of Toontown and make all Toons go sad for good.',
     "There was no way we could have let that happen, so we built a time machine, and sent every Toon back in time to OToontown, where Cogs didn't exist yet.",
     "The Cogs completely took over present day Toontown, and turned it into what they wanted it to be - a business metropolis.",
     'Toons happily live and play in OToontown now, but we want to learn about present day Toontown...',
     ' ...or as we now call it, CogTropolis.',
     "We've built time machines that send Toons back to CogTropolis to fight Cogs and to see what the Cogs have done.",
     "We know that the Cogs took over Toontown and turned it into a grey business city, but we don't know how they did it.",
     "Shopkeepers around OToontown will reward you for finding evidence that may help solve the mystery of how the Cogs turned Toontown into CogTropolis.",
     "Before you are able to head to CogTropolis, you need to be trained for battle.",
     "The Cogs have become much more skilled battlers and no longer wait for you to throw a gag before attacking you.",
     "This is much more difficult for Toons, and it may take some time to get used to.",
     "I'm going to give you 2 gags to start...",
     "A cupcake, and a squirting flower.",
     "Equip Gags in your loadout to use by pressing the corresponding key on your keyboard.",
     "You can use or throw the Gag that you have equipped by pressing the ALT key.",
     "Also, use the Arrow Keys on your keyboard to move, and press CTRL to jump.",
     "I'm going to summon one of our dummy bots for you to practice battling.",
     "Click your mouse when you're ready."]
    GUIDE_PT2_INFO = ["Now it'll get a tad bit tougher.", "This next dummy bot will be walking around.",
     "This will test your aiming skills.", "Click your mouse when you're ready."]
    GUIDE_PT3_INFO = ["This final dummy bot will walk around and try to attack you at times.", "Defeat this Cog to continue on to the next part of the tutorial."]
    GUIDE_DONE = ["Great!", "Did you know that Cog Invasion Online Alpha allows you to use any Gag that you want?",
     "Just use the Gags page in your Shticker Book to swap out the Gags that you want to be able to use!",
     "Also during Alpha testing, your Toon will start off with 5000 jellybeans and 100 Laff points.",
     "If you're looking to fight some Cogs, hop on the Trolley in the playgrounds to be teleported to CogTropolis!",
     "Each playground has a different difficulty of Cogs, so be careful!",
     "You can only fight Cogs in Toontown Central, Minnie's Melodyland, Donald's Dock, and Donald's Dreamland at the moment.",
     "You can also visit the Minigame Area using your Shticker Book to play some fun minigames!",
     "These games are best to play with other Toons!",
     "Remember, if you find any bugs or strange things during gameplay, you can go to the Contact Us page at coginvasion.com to report the issue.",
     "Have fun!"]
    #GUIDE_DONE = ["Wow, you did great!", "You're definitely ready for battle in CogTropolis.", "Click your mouse to head to OToontown."]
    GUIDE_START_TRAINING = "Alright! Let's do this!"

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('TutorialFSM', [State.State('off', self.enterOff, self.exitOff),
         State.State('newPlayerEmerge', self.enterPlayerEmerge, self.exitPlayerEmerge, ['off', 'introSpeech']),
         State.State('introSpeech', self.enterGuideIntroSpeech, self.exitGuideIntroSpeech, ['off', 'introSpeech2Training']),
         State.State('introSpeech2Training', self.enterIntroSpeech2Training, self.exitIntroSpeech2Training, ['off', 'training1']),
         State.State('training1', self.enterTrainingPT1, self.exitTrainingPT1, ['off', 'training2info']),
         State.State('training2info', self.enterTraining2Info, self.exitTraining2Info, ['off', 'training2']),
         State.State('training2', self.enterTrainingPT2, self.exitTrainingPT2, ['off', 'training3info']),
         State.State('training3info', self.enterTraining3Info, self.exitTraining3Info, ['off', 'training3']),
         State.State('training3', self.enterTrainingPT3, self.exitTrainingPT3, ['off', 'trainingDone']),
         State.State('trainingDone', self.enterTrainingDone, self.exitTrainingDone, ['off', 'leaveTutorial']),
         State.State('leaveTutorial', self.enterLeaveTutorial, self.exitLeaveTutorial, ['off'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.dnaStore = DNAStorage()
        self.streetGeom = None
        self.sky = None
        self.skyUtil = SkyUtil()
        self.guide = None
        self.music = None
        self.battleMusic = None
        self.playerCamPos = None
        self.playerCamHpr = None

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def introStuff(self):
        base.localAvatar.getGeomNode().hide()
        base.localAvatar.setPos(0, 0, -0.5)
        base.localAvatar.setHpr(0, 0, 0)
        self.guide.setPos(self.GUIDE_START_POS)
        self.guide.headsUp(base.localAvatar)
        base.localAvatar.attachCamera()

    def enterPlayerEmerge(self):
        self.introStuff()
        self.guide.loop('neutral')
        base.transitions.irisIn()
        base.taskMgr.doMethodLater(1.0, self.__playerEmerge, 'playerEmergeTask')

    def __playerEmerge(self, task):
        base.localAvatar.setAnimState('teleportIn', callback = self.__playerEmergeFinished)
        return Task.done

    def __playerEmergeFinished(self):
        base.localAvatar.setAnimState('neutral')
        self.fsm.request('introSpeech')

    def exitPlayerEmerge(self):
        base.localAvatar.detachCamera()
        base.taskMgr.remove('playerEmergeTask')
        base.transitions.noTransitions()

    def enterGuideIntroSpeech(self):
        base.localAvatar.attachCamera()
        renderPos = base.camera.getPos(render)
        renderHpr = base.camera.getHpr(render)
        base.localAvatar.detachCamera()
        endPos = base.localAvatar.getPos(render) + (0, 0, 4)
        base.camera.setPos(endPos)
        base.camera.lookAt(self.guide, 0, 0, 3)
        endHpr = base.camera.getHpr(render)
        base.camera.setPos(renderPos)
        base.camera.setHpr(renderHpr)
        self.chatIndex = -1
        self.doNextIntroSpeech()
        self.camMoveTrack = Sequence(Parallel(LerpPosInterval(base.camera, duration = 3.0, pos = endPos,
                                     startPos = renderPos, blendType = 'easeOut'),
                                     LerpQuatInterval(base.camera, duration = 3.0, hpr = endHpr,
                                     startHpr = renderHpr, blendType = 'easeOut')),
                                     Func(base.localAvatar.getGeomNode().hide))
        self.camMoveTrack.start()

    def __finishedReadingGuideIntroSpeech(self):
        self.guide.autoClearChat = True
        self.guide.setChat(self.GUIDE_START_TRAINING)
        self.fsm.request('introSpeech2Training')

    def doNextIntroSpeech(self):
        self.chatIndex += 1
        if self.chatIndex >= len(self.GUIDE_INTRO_SPEECH):
            self.__finishedReadingGuideIntroSpeech()
            return
        self.guide.setChat(self.GUIDE_INTRO_SPEECH[self.chatIndex])
        Sequence(Wait(0.1), Func(self.acceptOnce, 'mouse1-up', self.doNextIntroSpeech)).start()

    def exitGuideIntroSpeech(self):
        self.camMoveTrack.finish()
        base.localAvatar.getGeomNode().show()
        del self.camMoveTrack
        del self.chatIndex

    def enterIntroSpeech2Training(self):
        startCamPos = base.camera.getPos(render)
        startCamHpr = base.camera.getHpr(render)
        base.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        base.localAvatar.attachCamera()
        endCamPos = base.camera.getPos(render)
        endCamHpr = base.camera.getHpr(render)
        base.localAvatar.detachCamera()
        startHpr = self.guide.getHpr(render)
        self.guide.headsUp(self.GUIDE_WATCH_POS)
        endHpr = self.guide.getHpr(render)
        self.guide.loop('run')
        self.camMoveIval = Parallel(LerpPosInterval(base.camera, duration = 2.0, pos = endCamPos,
                                    startPos = startCamPos, blendType = 'easeOut'),
                                    LerpQuatInterval(base.camera, duration = 2.0, hpr = endCamHpr,
                                    startHpr = startCamHpr, blendType = 'easeOut'),
                                    Sequence(LerpPosInterval(self.guide, duration = 2.0, pos = self.GUIDE_WATCH_POS,
                                            startPos = self.guide.getPos(render)),
                                            Func(self.guide.loop, 'walk'),
                                            LerpHprInterval(self.guide, duration = 1.0, hpr = self.GUIDE_WATCH_HPR,
                                            startHpr = endHpr),
                                            Func(self.guide.loop, 'neutral')),
                                    LerpHprInterval(self.guide, duration = 1.0, hpr = endHpr, startHpr = startHpr))
        self.camMoveIval.setDoneEvent('introSpeech2TrainingDone')
        self.acceptOnce('introSpeech2TrainingDone', self.__handleIS2TDone)
        self.camMoveIval.start()

    def __handleIS2TDone(self):
        self.fsm.request('training1')

    def exitIntroSpeech2Training(self):
        self.ignore('introSpeech2TrainingDone')
        self.camMoveIval.finish()
        del self.camMoveIval

    def makeWhisper(self, msg):
        whisper = WhisperPopup(msg, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)

    def enterTrainingPT1(self):
        self.music.stop()
        base.playMusic(self.battleMusic, volume = 0.9, looping = 1)
        self.sendUpdate('makeSuit', [0])
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.startBlink()
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.collisionsOn()
        base.localAvatar.enableAvatarControls()
        base.localAvatar.enableGags(1)
        base.localAvatar.showGagButton()
        base.localAvatar.startTrackAnimToSpeed()
        self.makeWhisper("This should be pretty simple. Just throw a gag at this dummy bot to defeat it.")

    def suitNoHealth(self, index):
        if index == 0:
            self.makeWhisper("Good job, {0}!".format(base.localAvatar.getName()))
        elif index == 1:
            self.makeWhisper("Wow, you're doing very well!")

    def suitExploded(self, index):
        if index == 0:
            self.makeWhisper("Pick up the jellybean that he dropped. You can use them to buy more gags for your Toon.")
        self.battleMusic.stop()
        base.playMusic(self.music, looping = 1, volume = 0.8)

    def pickedUpJellybean(self):
        if self.fsm.getCurrentState().getName() == 'training1':
            self.fsm.request('training2info')
        elif self.fsm.getCurrentState().getName() == 'training2':
            self.fsm.request('training3info')
        elif self.fsm.getCurrentState().getName() == 'training3':
            self.fsm.request('trainingDone')

    def exitTrainingPT1(self):
        base.localAvatar.lastState = None
        base.localAvatar.disableAvatarControls()
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.stopBlink()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()
        base.localAvatar.disableGags()
        base.localAvatar.stopTrackAnimToSpeed()
        base.localAvatar.hideGagButton()

    def enterTraining2Info(self):
        base.camera.setPos(3.09, 37.16, 3.93)
        base.camera.setHpr(225, 0, 0)
        self.guide.autoClearChat = False
        self.chatIndex = -1
        self.doNextTraining2Speech()

    def __finishedReadingGuideTraining2Speech(self):
        self.guide.autoClearChat = True
        self.guide.clearChat()
        self.fsm.request('training2')

    def doNextTraining2Speech(self):
        self.chatIndex += 1
        if self.chatIndex >= len(self.GUIDE_PT2_INFO):
            self.__finishedReadingGuideTraining2Speech()
            return
        self.guide.setChat(self.GUIDE_PT2_INFO[self.chatIndex])
        Sequence(Wait(0.1), Func(self.acceptOnce, 'mouse1-up', self.doNextTraining2Speech)).start()

    def exitTraining2Info(self):
        base.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        del self.chatIndex

    def enterTrainingPT2(self):
        self.music.stop()
        base.playMusic(self.battleMusic, volume = 0.9, looping = 1)
        self.sendUpdate('makeSuit', [1])
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.startBlink()
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.collisionsOn()
        base.localAvatar.enableAvatarControls()
        base.localAvatar.enableGags(1)
        base.localAvatar.showGagButton()
        base.localAvatar.startTrackAnimToSpeed()

    def exitTrainingPT2(self):
        base.localAvatar.lastState = None
        base.localAvatar.disableAvatarControls()
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.stopBlink()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()
        base.localAvatar.disableGags()
        base.localAvatar.stopTrackAnimToSpeed()
        base.localAvatar.hideGagButton()

    def enterTraining3Info(self):
        base.camera.setPos(3.09, 37.16, 3.93)
        base.camera.setHpr(225, 0, 0)
        self.guide.autoClearChat = False
        self.chatIndex = -1
        self.doNextTraining3Speech()

    def __finishedReadingGuideTraining3Speech(self):
        self.guide.autoClearChat = True
        self.guide.clearChat()
        self.fsm.request('training3')

    def doNextTraining3Speech(self):
        self.chatIndex += 1
        if self.chatIndex >= len(self.GUIDE_PT3_INFO):
            self.__finishedReadingGuideTraining3Speech()
            return
        self.guide.setChat(self.GUIDE_PT3_INFO[self.chatIndex])
        Sequence(Wait(0.1), Func(self.acceptOnce, 'mouse1-up', self.doNextTraining3Speech)).start()

    def exitTraining3Info(self):
        base.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        del self.chatIndex

    def enterTrainingPT3(self):
        self.music.stop()
        base.playMusic(self.battleMusic, volume = 0.9, looping = 1)
        self.sendUpdate('makeSuit', [2])
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.startBlink()
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.collisionsOn()
        base.localAvatar.enableAvatarControls()
        base.localAvatar.enableGags(1)
        base.localAvatar.showGagButton()
        base.localAvatar.startTrackAnimToSpeed()

    def exitTrainingPT3(self):
        base.localAvatar.lastState = None
        base.localAvatar.disableAvatarControls()
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.stopBlink()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()
        base.localAvatar.disableGags()
        base.localAvatar.stopTrackAnimToSpeed()
        base.localAvatar.hideGagButton()

    def enterTrainingDone(self):
        base.camera.setPos(3.09, 37.16, 3.93)
        base.camera.setHpr(225, 0, 0)
        self.guide.autoClearChat = False
        self.chatIndex = -1
        self.doNextTrainingDoneSpeech()

    def __finishedReadingGuideTrainingDoneSpeech(self):
        self.guide.autoClearChat = True
        self.guide.clearChat()
        self.fsm.request('leaveTutorial')

    def doNextTrainingDoneSpeech(self):
        self.chatIndex += 1
        if self.chatIndex >= len(self.GUIDE_DONE):
            self.__finishedReadingGuideTrainingDoneSpeech()
            return
        self.guide.setChat(self.GUIDE_DONE[self.chatIndex])
        Sequence(Wait(0.1), Func(self.acceptOnce, 'mouse1-up', self.doNextTrainingDoneSpeech)).start()

    def exitTrainingDone(self):
        base.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        del self.chatIndex

    def enterLeaveTutorial(self):
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.b_setAnimState('teleportOut', callback = self.__teleOutDone)

    def __teleOutDone(self):
        zoneId = CIGlobals.ToontownCentralId
        hoodId = CIGlobals.ToontownCentral
        whereName = 'playground'
        avId = base.localAvatar.doId
        loaderName = 'safeZoneLoader'
        self.sendUpdate('finishedTutorial')
        self.cr.playGame.load()
        self.cr.playGame.enter(hoodId, zoneId, base.localAvatar.doId)

    def exitLeaveTutorial(self):
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        base.transitions.fadeScreen(0.0)
        self.guide = Toon(base.cr)
        self.guide.autoClearChat = False
        self.guide.parseDNAStrand(NPCGlobals.NPC_DNA[self.GUIDE_NAME])
        self.guide.setName(self.GUIDE_NAME)
        self.guide.generateToon()
        self.guide.nametag.setNametagColor(NametagGlobals.NametagColors[NametagGlobals.CCNPC])
        self.guide.nametag.setActive(0)
        self.guide.nametag.updateAll()
        self.guide.startBlink()
        self.guide.reparentTo(render)
        base.localAvatar.reparentTo(render)
        loader.loadDNAFile(self.dnaStore, 'phase_3.5/dna/storage_tutorial.pdna')
        node = loader.loadDNAFile(self.dnaStore, 'phase_3.5/dna/tutorial_street.pdna')
        if node.getNumParents() == 1:
            self.streetGeom = NodePath(node.getParent(0))
            self.streetGeom.reparentTo(hidden)
        else:
            self.streetGeom = hidden.attachNewNode(node)
        self.streetGeom.flattenMedium()
        gsg = base.win.getGsg()
        if gsg:
            self.streetGeom.prepareScene(gsg)
        self.streetGeom.reparentTo(render)
        self.streetGeom.setPos(20.5, -20, 0)
        self.streetGeom.setH(90)
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky.bam')
        self.skyUtil.startSky(self.sky)
        self.sky.reparentTo(camera)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)
        self.music = base.loadMusic('phase_3.5/audio/bgm/TC_SZ.mid')
        base.playMusic(self.music, volume = 0.8, looping = 1)
        self.battleMusic = base.loadMusic('phase_3.5/audio/bgm/encntr_general_bg.mid')
        self.fsm.request('newPlayerEmerge')
        base.localAvatar.inTutorial = True

    def disable(self):
        self.fsm.requestFinalState()
        del self.fsm
        if self.guide:
            self.guide.disable()
            self.guide.delete()
            self.guide = None
        if self.streetGeom:
            self.streetGeom.removeNode()
            self.streetGeom = None
        if self.sky:
            self.sky.removeNode()
            self.sky = None
        if self.music:
            self.music.stop()
            self.music = None
        if self.battleMusic:
            self.battleMusic.stop()
            self.battleMusic = None
        self.dnaStore.reset_nodes()
        self.dnaStore.reset_hood_nodes()
        self.dnaStore.reset_place_nodes()
        self.dnaStore.reset_hood()
        self.dnaStore.reset_fonts()
        self.dnaStore.reset_DNA_vis_groups()
        self.dnaStore.reset_textures()
        self.dnaStore.reset_block_numbers()
        self.dnaStore.reset_block_zones()
        self.dnaStore.reset_suit_points()
        self.dnaStore = None
        self.skyUtil = None
        base.localAvatar.inTutorial = False
        DistributedObject.disable(self)

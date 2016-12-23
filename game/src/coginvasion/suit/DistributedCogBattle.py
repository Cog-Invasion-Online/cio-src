# Filename: DistributedCogBattle.py
# Created by:  blach (11Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.gui.DirectGui import DirectWaitBar, DGG, DirectFrame, OnscreenText
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.globals import CIGlobals, ChatGlobals
from src.coginvasion.gui.WhisperPopup import WhisperPopup
from src.coginvasion.minigame.Timer import Timer
from src.coginvasion.nametag import NametagGlobals
import CogBattleGlobals

class DistributedCogBattle(DistributedObject):
    notify = directNotify.newCategory("DistributedCogBattle")
    DNCData = {
        0: [
            [(-50, 98.73, 0.40), (351.31, 0.00, 0.00), 1.25],
            [(-41.07, 97.20, 0.40), (350.34, 0.00, 0.00), 1.25],
            [(-152.73, -0.58, 0.40), (90.00, 0, 0), 1.25],
            [(-152.73, 8.81, 0.40), (85.30, 0, 0), 1.25],
            [(34.34, -157.19, 2.95), (150.75, 0, 0), 1.25],
            [(26.21, -152.66, 2.95), (147.09, 0, 0), 1.25]
        ],

        1: [],
        2: [],
        5: []
    }

    def __init__(self, cr):
        try:
            self.DistributedCogBattle_initialized
            return
        except:
            self.DistributedCogBattle_initialized = 1
        DistributedObject.__init__(self, cr)
        self.hoodIndex = None
        self.totalCogs = None
        self.cogsRemaining = None
        self.cogProgressBar = None
        self.DNCSigns = []
        self.introMessageSeq = None
        self.victorySeq = None
        self.turretManager = None
        self.isGettingBeans = False
        self.getBeansLabel = OnscreenText(text = "Hurry and pick up all of the jellybeans!", fg = (1, 1, 1, 1),
            shadow = (0, 0, 0, 1), pos = (0, 0.7), font = CIGlobals.getMinnieFont())
        self.getBeansLabel.hide()
        self.timer = Timer()
        self.timer.setZeroCommand(self.getBeansTimeUp)
        # Give toons 30 seconds to get the beans at the end.
        self.timer.setInitialTime(60)
        self.endMusic = base.loadMusic('phase_7/audio/bgm/encntr_toon_winning_indoor.mid')
        self.balloonSound = base.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg')

    def d_left(self):
        self.sendUpdate('iLeft')

    def monitorHP(self, task):
        if base.localAvatar.getHealth() < 1:
            taskMgr.doMethodLater(7.0, self.diedTask, self.uniqueName('diedTask'))
            return task.done
        return task.cont

    def diedTask(self, task):
        self.d_left()
        return task.done

    def setTurretManager(self, tmgr):
        self.turretManager = tmgr

    def getTurretManager(self):
        return self.turretManager

    def getTurretCount(self):
        avatars = self.cr.doFindAll('DistributedToon')
        turrets = 0

        if self.turretManager:
            if self.turretManager.getTurret():
                turrets += 1

        if base.localAvatar.getPUInventory()[0] > 0:
            turrets += 1

        for avatar in avatars:
            if avatar.zoneId == base.localAvatar.zoneId:
                battle = avatar.getMyBattle()
                if avatar.getPUInventory()[0] > 0:
                    turrets += 1

                if battle:
                    if battle.getTurretManager():
                        if battle.getTurretManager().getTurret():
                            turrets += 1
        return turrets

    def victory(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        base.localAvatar.b_setAnimState('win')
        self.victorySeq = Sequence(Wait(5.0), Func(self.finishVictory))
        self.victorySeq.start()

    def finishVictory(self):
        # Give the players some time to pick up jellybeans before they leave.
        self.cr.playGame.getPlace().fsm.request('walk')
        self.cr.playGame.hood.loader.music.stop()
        base.playMusic(self.endMusic, volume = 0.8, looping = 1)
        self.timer.load()
        self.timer.startTiming()
        self.getBeansLabel.show()
        base.playSfx(self.balloonSound)

    def getBeansTimeUp(self):
        self.timer.unload()
        self.getBeansLabel.hide()
        hoodId = self.cr.playGame.hood.hoodId
        zoneId = CogBattleGlobals.HoodIndex2HoodId[self.getHoodIndex()]
        requestStatus = {'zoneId': zoneId,
                    'hoodId': hoodId,
                    'where': 'playground',
                    'avId': base.localAvatar.doId,
                    'loader': 'safeZoneLoader',
                    'shardId': None,
                    'how': 'teleportIn'}
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])

    def setTotalCogs(self, num):
        self.totalCogs = num

    def getTotalCogs(self):
        return self.totalCogs

    def setCogsRemaining(self, num):
        self.cogsRemaining = num
        if self.cogProgressBar:
            self.__updateProgressBar()

    def getCogsRemaining(self):
        return self.cogsRemaining

    def setHoodIndex(self, index):
        self.hoodIndex = index

    def getHoodIndex(self):
        return self.hoodIndex

    def startPlacePoll(self):
        taskMgr.add(self.__placePoll, "DistributedCogBattle-placePoll")

    def __placePoll(self, task):
        # Wait for the place to come out of None
        if self.cr.playGame.getPlace() != None:
            self.sendUpdate("arrived", [])
            self.constructArea()
            self.createInterface()
            self.__doIntroMessages()
            return task.done
        else:
            return task.cont

    def stopPlacePoll(self):
        taskMgr.remove("DistributedCogBattle-placePoll")

    def createInterface(self):
        self.cogProgressBar = DirectWaitBar(pos = (0, 0, -0.9),
            relief = DGG.RAISED, scale = 0.6, frameColor = (1, 0.5, 0.3, 0.75),
            barColor = (1, 0.25, 0.25, 0.5), value = 0, range = self.getTotalCogs(), text = "", text_scale = 0.08)
        self.__updateProgressBar()

    def __updateProgressBar(self):
        self.cogProgressBar.update(self.getCogsRemaining())
        self.cogProgressBar['text'] = "{0}/{1} {2} Remaining".format(self.getCogsRemaining(), self.getTotalCogs(), CIGlobals.Suits)

    def destroyInterface(self):
        if self.cogProgressBar:
            self.cogProgressBar.destroy()
            self.cogProgressBar = None

    def createBossGui(self):
        self.destroyInterface()
        backgroundGui = loader.loadModel('phase_5/models/cogdominium/tt_m_gui_csa_flyThru.bam')
        backgroundGui.find('**/chatBubble').removeNode()
        bg = backgroundGui.find('**/background')
        bg.setScale(5.2)
        bg.setPos(0.14, 0, -0.6667)
        bg.reparentTo(aspect2d)
        self.frame = DirectFrame(geom = bg, relief = None, pos = (0.2, 0, -0.6667))

    def constructArea(self):
        for data in self.DNCData[self.hoodIndex]:
            dnc = loader.loadModel("phase_3.5/models/props/do_not_cross.egg")
            dnc.setPos(*data[0])
            dnc.setHpr(*data[1])
            dnc.setScale(data[2])
            dnc.reparentTo(render)
            self.DNCSigns.append(dnc)

    def deconstructArea(self):
        for dnc in self.DNCSigns:
            dnc.removeNode()

    def createWhisper(self, msg):
        whisper = WhisperPopup('Toon HQ: ' + msg, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)

    def __doIntroMessages(self):
        self.introMessageSeq = Sequence(name = "DistributedCogBattle-introMessageSeq")
        self.introMessageSeq.append(Func(self.createWhisper, "Welcome, Toons! The Cogs will be here soon, so get prepared!"))
        self.introMessageSeq.append(Wait(7.5))
        self.introMessageSeq.append(Func(self.createWhisper, "The pink bar at the bottom of the screen shows the amount of Cogs remaining to defeat."))
        self.introMessageSeq.append(Wait(8.5))
        self.introMessageSeq.append(Func(self.createWhisper, "Purchase gags from Goofy at the Gag Shop to restock your used gags."))
        self.introMessageSeq.append(Wait(7.5))
        self.introMessageSeq.append(Func(self.createWhisper, "Purchase battle tools from Coach at Coach's Battle Shop in between invasions."))
        self.introMessageSeq.setDoneEvent(self.introMessageSeq.getName())
        self.acceptOnce(self.introMessageSeq.getDoneEvent(), self.__introMessagesDone)
        self.introMessageSeq.start()

    def __introMessagesDone(self):
        if self.introMessageSeq:
            self.introMessageSeq.finish()
            self.introMessageSeq = None

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        base.localAvatar.setMyBattle(self)
        self.startPlacePoll()
        taskMgr.add(self.monitorHP, "DCB.monitorHP")

    def disable(self):
        taskMgr.remove("DCB.monitorHP")
        taskMgr.remove(self.uniqueName('diedTask'))
        self.endMusic.stop()
        self.endMusic = None
        self.getBeansLabel.destroy()
        self.getBeansLabel = None
        self.timer.unload()
        self.timer.cleanup()
        self.timer = None
        self.balloonSound = None
        self.turretManager = None
        base.localAvatar.setMyBattle(None)
        self.stopPlacePoll()
        self.deconstructArea()
        self.destroyInterface()
        if self.victorySeq:
            self.victorySeq.pause()
            self.victorySeq = None
        self.hoodIndex = None
        self.DNCSigns = None
        self.totalCogs = None
        self.cogsRemaining = None
        if self.introMessageSeq:
            self.introMessageSeq.pause()
            self.introMessageSeq = None
        DistributedObject.disable(self)

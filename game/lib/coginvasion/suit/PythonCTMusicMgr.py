# Filename: PythonCTMusicMgr.py
# Created by:  blach (28Jun16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

import ccoginvasion

import random

class PythonCTMusicManager(DirectObject, ccoginvasion.CTMusicManager):
    notify = directNotify.newCategory("PythonCTMusicManager")

    # Wait this long to begin monitoring our situation number so
    # the intro clip has time to play.
    TimeUntilBeginMonitoring = 10.0

    ArrestingYouRange = [-50, -41]
    GettingWorseRange = [-40, -21]
    FiftyFiftyRange = [-20, 20]
    RunningAwayRange = [21, 35]
    HSpdClDwnRange = [36, 45]
    StcClDwnRange = [46, 50]

    StyleChangeTRange = [5, 30]

    IntroOrchestraFromLocatedStartPoint = [43, 44]

    HpPercUpdateIval = 5.0
    # How big does the hp perc difference have to be after 5 seconds to be considered urgent?
    UrgentPercDiff = 0.2

    def __init__(self, suitMgr):
        # Initialize C++ layer.
        ccoginvasion.CTMusicManager.__init__(self)

        songs = []
        for i in xrange(base.config.GetInt('ctmusic-numsongs', 1)):
            songs.append("encntr_nfsmw_bg_" + str(i + 1))
        songName = random.choice(songs)
        print songName
        self.set_song_name(songName)

        self.suitMgr = suitMgr

        self.lastStyleChangeT = 0.0
        self.styleChangeIval = 0.0

        self.shouldSwitchToIntro = False
        self.switchToIntroPoint = 0

        self.currHpPerc = 1.0
        self.lastHpPercUpdateT = 0.0

        self.urgentEvent = False

        # How many cogs are currently chasing me down?
        self.numChasers = 0
        # How many cogs are in range of me?
        self.numInRange = 0

    @staticmethod
    def getCogInRangeDistance():
        # What would we consider in range?
        return 20.0

    @staticmethod
    def getCogChasingEvent():
        return 'CogEvent::Chasing'

    def __handleCogChasing(self):
        self.numChasers += 1

    @staticmethod
    def getCogLostTargetEvent():
        return 'CogEvent::lostTarget'

    def __handleCogLostTarget(self):
        self.numChasers -= 1

    @staticmethod
    def getCogInRangeEvent():
        return 'CogEvent::in-range'

    def __handleCogInRange(self):
        # A cog might be chasing me.
        self.numInRange += 1

    @staticmethod
    def getCogOutOfRangeEvent():
        return 'CogEvent::out-of-range'

    def __handleCogOutOfRange(self):
        # A cog went out of range... phew!
        self.numInRange -= 1

    @staticmethod
    def getLocalAvDiedEvent():
        return 'LocalAvDied'

    def __handleLocalAvDied(self):
        self.play_arrested()

    def __is_in_range(self, therange):
        return (self.situationNumber >= therange[0] and self.situationNumber <= therange[1])

    def pick_style(self):
        return random.choice(["_base", "_orchestra"])

    def get_hp_perc(self):
        return float(base.localAvatar.getHealth()) / float(base.localAvatar.getMaxHealth())

    def __monitor_situation_task(self, task):

        currTime = globalClock.getFrameTime()

        shouldChangeStyle = (currTime - self.lastStyleChangeT) >= self.styleChangeIval

        if (currTime - self.lastHpPercUpdateT) >= self.HpPercUpdateIval:
            if self.urgentEvent is True:
                self.urgentEvent = False
            newPerc = self.get_hp_perc()
            percDiff = self.currHpPerc - newPerc
            if percDiff >= self.UrgentPercDiff:
                # Quick and big change in HP over 5 seconds!
                self.urgentEvent = True
            self.currHpPerc = newPerc
            self.lastHpPercUpdateT = globalClock.getFrameTime()

        extension = self.pick_style()

        if (self.urgentEvent is True):
            # We've got an urgent event!
            self.set_clip_request("arresting_you")

        elif (self.numChasers == 0 and self.numInRange == 0):
            # We've got nothing.
            self.set_clip_request("high_speed_cooldown" + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("high_speed_cooldown" + extension)
        elif (self.numChasers > 0 and self.numInRange == 0):
            # We've got some chasers, but they aren't in range. Maybe we're running away from them.
            self.set_clip_request("running_away" + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("running_away" + extension)
        elif (self.numChasers > 0 and self.numInRange > 0 and self.numInRange <= 5) or (self.numChasers == 0 and self.numInRange > 0):
            # Hmm, I would say things are about 50/50.
            clip = "5050"
            if self.get_clip_name() == "5050":
                shouldChange = random.randint(0, 15)
                if shouldChange == 0:
                    clip = "located"
            elif self.get_clip_name() == "located":
                shouldChange = random.randint(0, 2)
                if shouldChange == 0:
                    clip = "5050"
            if self.get_hp_perc() <= 0.35:
                # We have low health, it is not 5050!
                if clip != "located":
                    clip = "getting_worse"
            self.set_clip_request(clip + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request(clip + extension)
        elif (self.numChasers > 0 and self.numInRange > 5 and self.numInRange <= 13):
            # Whoa, things are getting a little heated up in here.
            self.set_clip_request("getting_worse" + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("getting_worse" + extension)

        if shouldChangeStyle:
            SCTR = PythonCTMusicManager.StyleChangeTRange
            self.styleChangeIval = random.randint(SCTR[0], SCTR[1])
            self.lastStyleChangeT = globalClock.getFrameTime()

        task.delayTime = 1.0
        return task.cont

    def start_music(self):
        ccoginvasion.CTMusicManager.start_music(self, self.pick_style())

        self.lastStyleChangeT = globalClock.getFrameTime()

        SCTR = PythonCTMusicManager.StyleChangeTRange
        self.styleChangeIval = random.randint(SCTR[0], SCTR[1])
        
        self.currHpPerc = self.get_hp_perc()
        self.lastHpPercUpdateT = globalClock.getFrameTime()

        self.accept(PythonCTMusicManager.getCogLostTargetEvent(), self.__handleCogLostTarget)
        self.accept(PythonCTMusicManager.getCogInRangeEvent(), self.__handleCogInRange)
        self.accept(PythonCTMusicManager.getCogChasingEvent(), self.__handleCogChasing)
        self.accept(PythonCTMusicManager.getCogOutOfRangeEvent(), self.__handleCogOutOfRange)
        self.acceptOnce(PythonCTMusicManager.getLocalAvDiedEvent(), self.__handleLocalAvDied)

        base.taskMgr.doMethodLater(
            PythonCTMusicManager.TimeUntilBeginMonitoring, self.__monitor_situation_task,
            self.suitMgr.uniqueName('monitorSituationTask'))

    def handle_part_done(self, partIndex):
        # PartIndex = the index of the part that just finished
        print "Python: handle_part_done"
        if self.shouldSwitchToIntro:
            print "Should switch"
            if self.switchToIntroPoint == partIndex:
                print "switching"
                self.set_clip_request("intro_orchestra_from_located")
                self.shouldSwitchToIntro = False
                self.switchToIntroPoint = 0

        ccoginvasion.CTMusicManager.handle_part_done(self, partIndex)

    def play_located(self):
        # This is basically an intro but to a new cog round.
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        self.shouldSwitchToIntro = random.choice([True, False])
        if self.shouldSwitchToIntro:
            self.switchToIntroPoint = random.choice(self.IntroOrchestraFromLocatedStartPoint)
        self.set_clip_request("located" + self.pick_style())
        base.taskMgr.doMethodLater(
            PythonCTMusicManager.TimeUntilBeginMonitoring, self.__monitor_situation_task,
            self.suitMgr.uniqueName('monitorSituationTask'))

    def play_cooldown(self):
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        clip = random.choice(["high_speed_cooldown_orchestra", "static_cooldown"])
        self.set_clip_request(clip)

    def play_arrested(self):
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        choices = []
        for i in xrange(4):
            choices.append("arrested_" + str(i + 1))
        clip = random.choice(choices)
        self.set_clip_request(clip)

    def play_evaded(self):
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        choices = []
        for i in xrange(8):
            choices.append("evaded_" + str(i + 1))
        clip = random.choice(choices)
        self.set_clip_request(clip)

    def stop_music(self):
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        self.ignore(PythonCTMusicManager.getCogLostTargetEvent())
        self.ignore(PythonCTMusicManager.getCogInRangeEvent())
        self.ignore(PythonCTMusicManager.getCogChasingEvent())
        self.ignore(PythonCTMusicManager.getCogOutOfRangeEvent())
        self.ignore(PythonCTMusicManager.getLocalAvDiedEvent())

        self.stop_clip()

    def cleanup(self):
        self.stop_music()
        self.shouldSwitchToIntro = None
        self.switchToIntroPoint = None
        self.suitMgr = None
        self.lastStyleChangeT = None
        self.styleChangeIval = None
        self.lastHpPercUpdateT = None
        self.currHpPerc = None
        self.numChasers = None
        self.numInRange = None

# Filename: TTSafeZoneLoader.py
# Created by:  blach (25Oct15)

from direct.actor.Actor import Actor

from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType
import SafeZoneLoader
import TTPlayground

import random

class TTSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = TTPlayground.TTPlayground
        self.pgMusicFilename = 'phase_4/audio/bgm/TC_nbrhood.mid'
        self.interiorMusicFilename = 'phase_3.5/audio/bgm/TC_SZ_activity.mid'
        self.battleMusicFile = 'phase_3.5/audio/bgm/encntr_general_bg.mid'
        self.invasionMusicFiles = [
            "phase_12/audio/bgm/BossBot_CEO_v1.mid",
            "phase_9/audio/bgm/encntr_suit_winning.mid"
        ]
        self.tournamentMusicFiles = [
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_1.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_2.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_3.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_4.ogg",
        ]
        self.bossBattleMusicFile = 'phase_7/audio/bgm/encntr_suit_winning_indoor.mid'
        self.dnaFile = 'phase_4/dna/new_ttc_sz.pdna'
        self.szStorageDNAFile = 'phase_4/dna/storage_TT_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_4/dna/winter_storage_TT_sz.pdna'
        self.telescope = None
        self.birdNoises = [
            'phase_4/audio/sfx/SZ_TC_bird1.ogg',
            'phase_4/audio/sfx/SZ_TC_bird2.ogg',
            'phase_4/audio/sfx/SZ_TC_bird3.ogg'
        ]
        self.trees = []

        base.wakeWaterHeight = -0.69

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.geom.find('**/ground_center').setBin('ground', 18)
        self.geom.find('**/ground_sidewalk').setBin('ground', 18)
        self.geom.find('**/ground').setBin('ground', 18)
        self.geom.find('**/ground_center_coll').setCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/ground_sidewalk_coll').setCollideMask(CIGlobals.FloorBitmask)
        for tree in self.geom.findAllMatches('**/prop_green_tree_*_DNARoot'):
            tree.wrtReparentTo(hidden)
            self.trees.append(tree)
            newShadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
            newShadow.reparentTo(tree)
            newShadow.setScale(1.5)
            newShadow.setBillboardAxis(2)
            newShadow.setColor(0, 0, 0, 0.5, 1)

        # Fix bank door trigger
        bank = self.geom.find('**/*toon_landmark_TT_bank_DNARoot')
        doorTrigger = bank.find('**/door_trigger*')
        doorTrigger.setY(doorTrigger.getY() - 1.0)

        self.telescope = Actor(self.geom.find('**/*animated_prop_HQTelescopeAnimatedProp*'),
                            {'chan': 'phase_3.5/models/props/HQ_telescope-chan.bam'}, copy=0)
        self.telescope.reparentTo(self.geom.find('**/tb20:toon_landmark_hqTT_DNARoot'))
        self.telescope.setPos(1, 0.46, 0)
        
        water = self.geom.find("**/pond_water")
        base.waterReflectionMgr.addWaterNode(water, base.wakeWaterHeight)

        self.geom.flattenMedium()

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)
        taskMgr.add(self.telescopeTask, "TTSafeZoneLoader-telescopeTask")

    def telescopeTask(self, task):
        if self.telescope:
            self.telescope.play("chan")
            task.delayTime = random.uniform(12.0, 16.0)
            return task.again
        else:
            return task.done

    def exit(self):
        taskMgr.remove("TTSafeZoneLoader-telescopeTask")
        SafeZoneLoader.SafeZoneLoader.exit(self)

    def unload(self):
        if self.telescope:
            self.telescope.cleanup()
            self.telescope = None
        for tree in self.trees:
            tree.removeNode()
        self.trees = None
        SafeZoneLoader.SafeZoneLoader.unload(self)

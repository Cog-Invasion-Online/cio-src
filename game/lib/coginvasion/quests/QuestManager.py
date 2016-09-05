# Filename: QuestManager.py
# Created by:  blach (29Ju15)

from direct.showbase.DirectObject import DirectObject

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import ZoneUtil

from QuestManagerBase import QuestManagerBase
import QuestNote
import Quests
from QuestGlobals import *
import Objectives

class QuestManager(QuestManagerBase):

    def makeQuestsFromData(self):
        QuestManagerBase.makeQuestsFromData(self, base.localAvatar)

    def getTaskInfo(self, objective, speech = False):
        """
        Returns a string that could be used as speech or for a quest note.
        It gives information about the quest and what you have to do.
        """

        taskInfo = ""

        if speech:
            # If it's speech, add the objective's header (e.g Defeat, Recover, Deliver) to the beginning of the sentence.
            taskInfo += objective.Header + " "

        if objective.goal > 1:
            taskInfo += "%d " % objective.goal
        else:
            taskInfo += "a "

        # Add objective specific task info
        taskInfo += objective.getTaskInfo()

        if objective.AreaSpecific:
            # This objective is sometimes area specific.
            if objective.area == Anywhere:
                taskInfo += "\nAnywhere" if not speech else " Anywhere"
            else:
                # Say what area the objective must be completed in.
                taskInfo += "\nin " + ZoneUtil.getHoodId(objective.area) if not speech else " in " + ZoneUtil.getHoodId(objective.area)

        if speech:
            # Always put a period at the end of the sentence if it's speech!
            taskInfo += "."

        return taskInfo

    def makeQuestNotes(self, quests = None):
        """
        Generates and returns a list of QuestNote objects that display information about the quests.
        You can specify a custom quest list. If you don't it will use the QuestManager's quest dictionary.
        """

        # This is what will be returned at the end. It's going to hold our QuestNotes we generate.
        notes = []

        if not quests:
            # A custom quest list was not specified, use our dictionary.
            quests = self.quests.values()

        for quest in quests:

            objective = quest.currentObjective

            note = QuestNote.QuestNote(quest.index)

            # Set the notes heading as the objective's Header (e.g Defeat, Recover, Deliver, Visit)
            if not objective.isComplete():
                heading = objective.Header
                note.setHeading(heading)
            else:
                note.setHeading(QuestNote.HDR_RETURN)

            taskInfo = None
            if not objective.type in [Objectives.VisitNPC, Objectives.VisitHQOfficer]:
                # Get task info.
                if not objective.isComplete():
                    taskInfo = self.getTaskInfo(objective)
                else:
                    if objective.goal > 1:
                        taskInfo = "%d " % objective.goal
                    else:
                        taskInfo = "a "
                    taskInfo += objective.getTaskInfo() + "\n"
                    if objective.assigner != 0:
                        taskInfo += "to %s\nat %s" % (CIGlobals.NPCToonNames[objective.assigner],
                                                      CIGlobals.zone2TitleDict[CIGlobals.NPCToonDict[objective.assigner][0]][0])
                    else:
                        taskInfo += "to an HQ Officer\nat a Toon HQ"

            elif objective.type == Objectives.VisitNPC:
                # Say the NPC name and the building of the NPC.
                nameOfNPC = CIGlobals.NPCToonNames[objective.npcId]
                placeOfNPC = CIGlobals.zone2TitleDict[objective.npcZone][0]
                taskInfo = nameOfNPC + "\nat " + placeOfNPC

            elif objective.type == Objectives.VisitHQOfficer:
                # Say it's an hq officer at Toon HQ
                taskInfo = "an HQ Officer\nat a Toon HQ"

            # Apply the task info
            note.setTaskInfo(taskInfo)

            progress = ""
            if objective.HasProgress:
                note.useProgressBar = True

                # This objective has progress (e.g 2 of 5 Defeated, 0 of 1 Recovered)
                if not objective.isComplete():
                    progress = objective.getProgressText()
                    note.setProgress(progress, objective.goal, objective.progress)
                else:
                    note.setCompleted(1)

            elif objective.type == Objectives.VisitNPC or (objective.isComplete() and objective.assigner != 0):
                # Show the street name and hood name of where this NPC is located.

                streetZone = ZoneUtil.getBranchZone(objective.npcZone)
                if streetZone % 1000 >= 100:
                    streetName = CIGlobals.BranchZone2StreetName[streetZone]
                else:
                    streetName = "the Playground"

                hoodName = ZoneUtil.getHoodId(streetZone, 1)

                progress = "on %s\nin %s" % (streetName, hoodName)

                note.setProgress(progress)

            elif objective.type == Objectives.VisitHQOfficer or (objective.isComplete() and objective.assigner == 0):
                # HQ officers are at any street and any playground.
                progress = "Any Street\nAny Playground"

                note.setProgress(progress)

            if objective.showAsComplete:
                note.setCompleted(1)

            note.setReward("For " + quest.reward.fillInDialogue())

            notes.append(note)

        return notes

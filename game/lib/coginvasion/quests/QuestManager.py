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

    # Returns a string that could be used as speech or for a quest note.
    # It gives information about the quest and what you have to do.
    def getTaskInfo(self, objective, speech = False):
        taskInfo = ""

        if speech:
            # If it's speech, add the objective's header (e.g Defeat, Recover, Deliver) to the beginning of the sentence.
            taskInfo += objective.Header + " "

        if objective.goal > 1:
            # If the goal is more than one, put the number.
            taskInfo += "%d " % objective.goal
        else:
            # If the goal is only one, but `a`.
            taskInfo += "a "

        # Add objective specific task info
        taskInfo += objective.getTaskInfo()

        if objective.AreaSpecific:
            # This objective is sometimes area specific.
            if objective.area == Anywhere:
                # The objective's area is anywhere. If it's not speech, make a new line and put Anywhere.
                # If it's speech, put a space and then Anywhere.
                taskInfo += "\nAnywhere" if not speech else " Anywhere"
            else:
                # Say what area the objective must be completed in.
                taskInfo += "\nin " + ZoneUtil.getHoodId(objective.area) if not speech else " in " + ZoneUtil.getHoodId(objective.area)

        if speech:
            # Always put a period at the end of the sentence if it's speech!
            taskInfo += "."

        return taskInfo

    # Generates and returns a list of QuestNote objects that display information about the quests.
    # You can specify a custom quest list. If you don't it will use the QuestManager's quest dictionary.
    def makeQuestNotes(self, quests = None):
        # This is what will be returned at the end. It's going to hold our QuestNotes we generate.
        notes = []

        if not quests:
            # A custom quest list was not specified, use our dictionary.
            quests = self.quests.values()

        for quest in quests:

            objective = quest.currentObjective

            # Create the QuestNote instance
            note = QuestNote.QuestNote(quest.index)

            # Set the notes heading as the objective's Header (e.g Defeat, Recover, Deliver, Visit)
            heading = objective.Header
            note.setHeading(heading)

            taskInfo = None
            if objective.type not in [Objectives.VisitNPC, Objectives.VisitHQOfficer]:
                # Get task info.
                taskInfo = self.getTaskInfo(objective)

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
                # This objective has progress (e.g 2 of 5 Defeated, 0 of 1 Recovered)
                if not objective.isComplete():
                    # The objective isn't complete so we will show the progress text.
                    progress = objective.getProgressText()
                    note.setProgress(progress)
                else:
                    # The objective is complete so we will make the quest note green and say completed.
                    note.setCompleted(1)

            elif objective.type == Objectives.VisitNPC:
                # Show the street name and hood name of where this NPC is located.

                streetZone = ZoneUtil.getBranchZone(objective.npcZone)
                if streetZone % 1000 >= 100:
                    streetName = CIGlobals.BranchZone2StreetName[streetZone]
                else:
                    streetName = "the Playground"

                hoodName = ZoneUtil.getHoodId(streetZone, 1)

                progress = "on %s\nin %s" % (streetName, hoodName)

                # Apply the progress text
                note.setProgress(progress)

            elif objective.type == Objectives.VisitHQOfficer:
                # HQ officers are at any street and any playground.
                progress = "Any Street\nAny Playground"

                # Apply the progress text
                note.setProgress(progress)

            # Get the reward dialogue from the reward class of the quest.
            note.setReward("For " + quest.reward.fillInDialogue())

            # Add this QuestNote to the list.
            notes.append(note)

        # Return our beautiful list of QuestNotes.
        return notes

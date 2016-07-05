# Filename: Quest.py
# Created by:  blach (29Jul15)
#
# Data holder for individual quests.

class Quest:

    def __init__(self, type, subject, area, reward, progress, goal, rewardValue, index):
        self.type = type
        self.subject = subject
        self.area = area
        self.reward = reward
        self.progress = progress
        self.goal = goal
        self.rewardValue = rewardValue
        self.index = index

    def isComplete(self):
        return self.progress >= self.goal

    def cleanup(self):
        del self.type
        del self.subject
        del self.area
        del self.reward
        del self.progress
        del self.goal
        del self.rewardValue

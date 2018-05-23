from lib.coginvasion.standalone.StandaloneToon import *

from lib.coginvasion.quest.Quest import Quest
from lib.coginvasion.quest.DeliverItemObjective import DeliverItemObjective
from lib.coginvasion.quest.VisitNPCObjective import VisitNPCObjective
from lib.coginvasion.quest.CogObjective import CogObjective
from lib.coginvasion.quest.RecoverItemObjective import RecoverItemObjective
from lib.coginvasion.quest.QuestReward import QuestReward
from lib.coginvasion.quest.QuestPoster import QuestPoster
from lib.coginvasion.quest import QuestGlobals
from lib.coginvasion.quest import RewardType

quest = Quest("The Hell Begins", 0, "3", [QuestReward(RewardType.LAFF_POINTS, 2)])#[QuestReward(RewardType.LAFF_POINTS, 3), QuestReward(RewardType.LAFF_POINTS, 2)])
quest.addObjective(CogObjective(quest, 2000, [], 10, name = 'Big Wig'))
#quest.addObjective(RecoverItemObjective(20, 'Powder', quest, [], 1000, name = 'Cold Caller'))
#quest.addObjective(VisitNPCObjective(3112, quest, ['Hello']))
#quest.addObjective(DeliverItemObjective(3326, "1 Pincher", quest, ['Hello!']))
poster = QuestPoster(quest)
poster.reparentTo(aspect2d)
poster.update()

run()
"""
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
"""

import test_base
import src.coginvasion.standalone.Standalone

model = loader.loadModel('phase_5.5/models/estate/terrain.bam')
model.reparentTo(render)

from panda3d.core import TransparencyAttrib
from src.coginvasion.shop.DistributedBattleShop import DistributedBattleShop
from src.coginvasion.shop.DistributedGagShop import DistributedGagShop

#bShop = DistributedBattleShop(base.cr)
#bShop.generate()
#bShop.setupClerk()
gShop = DistributedGagShop(base.cr)
base.cr.createDistributedObject(distObj = gShop)
gShop.setParent(2)
gShop.reparentTo(render)
#gShop.clerk.reparentTo(gShop)
print gShop.getParent()
#gShop.reparentTo(render)

def processChildren(node):
	if len(node.getChildren()) > 0:
		for child in node.getChildren():
			print 'Applying transparency to node: {0}.'.format(child.getName())
			print child.getTexture()
			child.setTransparency(TransparencyAttrib.M_multisample, 1)
			child.setDepthOffset(1, 1)
			#child.setBin('shadow', 19)
			child.clearModelNodes()
			child.flattenStrong()
			print 'Applied bin'
			processChildren(child)

#dBase.setBin('ground', 18)
#processChildren(dBase)
#print 'Applied fix'

gShop.clerk.reparentTo(gShop)
base.oobe()

base.startDirect()
base.run()
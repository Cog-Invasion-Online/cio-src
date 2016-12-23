"""

  Filename: DistributedWinterCoachActivity.py
  Created by: DecodedLogic (14Nov15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNode import DistributedNode
from pandac.PandaModules import NodePath, CollisionSphere, CollisionNode

from src.coginvasion.toon.Toon import Toon
from src.coginvasion.globals import CIGlobals
from src.coginvasion.npc.NPCGlobals import NPC_DNA
from src.coginvasion.holiday.HolidayManager import HolidayGlobals

class DistributedWinterCoachActivity(DistributedNode):
    notify = directNotify.newCategory('DistributedWinterCoachActivity')
    
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'winter_coach')
        self.cr = cr
        self.coach = None
        self.wheelBarrow = None
        self.coachNP = None
        
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.__initInteractCollisions('coachSphere' + str(self.doId))
        self.buildCoach()
        self.setParent(CIGlobals.SPRender)
        
    def greetAvatar(self, avatarName):
        self.coach.setChat(HolidayGlobals.COACH_GREETING % (avatarName))
        
    def buildCoach(self):
        # Let's load up Coach
        self.coach = Toon(self.cr)
        self.coach.setName('Coach')
        self.coach.setDNAStrand(NPC_DNA['Coach'])
        self.coach.reparentTo(self)
        self.coach.animFSM.request('neutral')
        
        # Let's load up the Wheel Barrow
        self.wheelBarrow = loader.loadModel('phase_5.5/models/estate/wheelbarrel.bam')
        self.wheelBarrow.find('**/dirt').setTexture(loader.loadTexture('winter/maps/sbhq_snow.png'), 1)
        self.wheelBarrow.reparentTo(self.coach)
        self.wheelBarrow.setX(-3.5)
        self.wheelBarrow.setH(90)
        
    def deleteCoach(self):
        if self.coach:
            # Delete Coach
            self.coach.disable()
            self.coach.delete()
            self.coach = None
            
            # Delete Wheelbarrow
            self.wheelBarrow.removeNode()
            self.wheelBarrow = None
        
    def __initInteractCollisions(self, colName):
        self.notify.debug('Setting up Coach collisions')
        collSphere = CollisionSphere(0, 0, 0, 5)
        collSphere.setTangible(0)
        collNode = CollisionNode(colName)
        collNode.addSolid(collSphere)
        collNode.setCollideMask(CIGlobals.WallBitmask)
        self.coachNP = self.attachNewNode(collNode)
        self.coachNP.setZ(3)
        self.acceptOnce('enter' + self.coachNP.node().getName(), self.__handleCollision)
        
    def __handleCollision(self, entry):
        self.notify.debug('Entered collision sphere.')
        self.d_requestEnter()
        
    def d_requestEnter(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestEnter', [])

    def d_requestExit(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestExit', [])
        
    def enterAccepted(self):
        self.d_requestExit()
        base.localAvatar.updateSnowballButton()
        
    def exitAccepted(self):
        self.cr.playGame.getPlace().fsm.request('walk')
        self.acceptOnce('enter' + self.coachNP.node().getName(), self.__handleCollision)
        
    def destroy(self):
        self.deleteCoach()
        self.coachNP = None

    def disable(self):
        DistributedNode.disable(self)
        self.destroy()

    def delete(self):
        DistributedNode.delete(self)
        self.destroy()
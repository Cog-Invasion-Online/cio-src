"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTNTAI.py
@author Brian Lach
@date June 15, 2018

"""

from DistributedPhysicsEntityAI import DistributedPhysicsEntityAI

class DistributedTNTAI(DistributedPhysicsEntityAI):
    
    def explode(self):
        # Go ahead and delete this object for the owner client.
        # Clients can't delete objects over the network, even
        # if they are the owner.
        sender = self.air.getMsgSender()
        self.air.clientRemoveSessionObject(sender, self.doId)
        self.requestDelete()

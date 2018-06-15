from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI

class ClientServicesManagerAI(DistributedObjectGlobalAI):

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

    def d_giveClientOwnershipOfObject(self, context, accId, doId, dclassNum):
        self.sendUpdate('giveClientOwnershipOfObject', [context, accId, doId, dclassNum])

    def clientObjectOwnershipGranted(self, context, accId, doId):
        self.air.district.temporaryObjectComplete(context, accId, doId)

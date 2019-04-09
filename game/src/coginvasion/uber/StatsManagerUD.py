from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

class StatsManagerUD(DistributedObjectGlobalUD):
    
    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        
"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTailorInterior.py
@author Maverick Liberty
@date August 11, 2015

"""

from src.coginvasion.hood import DistributedToonInterior

class DistributedTailorInterior(DistributedToonInterior.DistributedToonInterior):
    
    def makeInterior(self, roomIndex=None):
        DistributedToonInterior.DistributedToonInterior.makeInterior(self, roomIndex=0)
        
"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedHPBarrel.py
@author Maverick Liberty
@date March 27, 2018

It seriously took me 2 years to add in toon-up barrels. SMH

"""

from DistributedRestockBarrel import DistributedRestockBarrel

class DistributedHPBarrel(DistributedRestockBarrel):
    
    def __init__(self, cr):
        DistributedRestockBarrel.__init__(self, cr)

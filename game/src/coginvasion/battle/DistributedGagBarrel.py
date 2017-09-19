"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagBarrel.py
@author Maverick Liberty
@date March 12, 2016

"""

from DistributedRestockBarrel import DistributedRestockBarrel

class DistributedGagBarrel(DistributedRestockBarrel):                 
    
    def __init__(self, cr):
        DistributedRestockBarrel.__init__(self, cr)
########################################
# Filename: DistributedGagBarrel.py
# Created by: DecodedLogic (12Mar16)
########################################

from DistributedRestockBarrel import DistributedRestockBarrel

class DistributedGagBarrel(DistributedRestockBarrel):
    
    def __init__(self, cr):
        DistributedRestockBarrel.__init__(self, cr)
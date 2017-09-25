"""

  Filename: RecoverHoodAI.py
  Created by: blach (03Apr15)

"""

from HoodAI import HoodAI
from panda3d.core import Point3
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit.DistributedDroppableCollectableIceCreamAI import DistributedDroppableCollectableIceCreamAI

class RecoverHoodAI(HoodAI):
    notify = directNotify.newCategory("RecoverHoodAI")
    maxIceCreams = 15
    iceCreamLocs = [
        Point3(24.77, 0.00, 11.71),
        Point3(10.99, 28.60, 4.25),
        Point3(51.23, 6.87, 8.00),
        Point3(44.50, -19.36, 8.46),
        Point3(92.33, -19.36, 0.02),
        Point3(92.33, 14.32, 4.25),
        Point3(8.05, -50.13, 4.16),
        Point3(49.36, -50.13, 5.10),
        Point3(82.02, -71.27, 0.00),
        Point3(22.85, 71.00, -0.01),
        Point3(47.72, 53.37, 0.02),
        Point3(91.21, 52.57, 0.02),
        Point3(1.65, 65.08, 4.79),
        Point3(-41.37, 62.30, 0.02),
        Point3(-33.17, 29.78, 2.33),
        Point3(-57.35, 14.62, 2.36),
        Point3(-57.35, -66.80, 3.95)
    ]
    
    def __init__(self, air):
        HoodAI.__init__(self, air, CIGlobals.RecoverAreaId,
            CIGlobals.RecoverArea)
        self.iceCreams = []
        self.startup()
        
    def startup(self):
        HoodAI.startup(self)
        self.notify.info("Creating ice creams...")
        for index in range(self.maxIceCreams):
            iceCream = DistributedDroppableCollectableIceCreamAI(self.air)
            iceCream.generateWithRequired(self.zoneId)
            pos = self.iceCreamLocs[index]
            x = pos.getX()
            y = pos.getY()
            z = pos.getZ()
            iceCream.d_setPos(x, y, z)
            iceCream.setDisabled(0)
            iceCream.b_setParent(CIGlobals.SPRender)
            self.iceCreams.append(iceCream)
            
    def shutdown(self):
        self.notify.info("Deleting ice creams...")
        for iceCream in self.iceCreams:
            iceCream.requestDelete()
            self.iceCreams.remove(iceCream)
            del iceCream
        del self.iceCreams
        HoodAI.shutdown(self)

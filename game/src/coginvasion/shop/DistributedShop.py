"""

  Filename: DistributedShop.py
  Created by: DecodedLogic (13Jul15)

"""

from direct.distributed.DistributedNode import DistributedNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.globals import CIGlobals
from src.coginvasion.shop.ItemType import ItemType
from panda3d.core import NodePath, CollisionSphere, CollisionNode
import abc

class DistributedShop(DistributedNode):
    notify = directNotify.newCategory('DistributedShop')

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'shop')
        self.cr = cr
        self.items = {}
        self.inShop = False
        self.clerk = None
        self.shopNP = None

    def addItem(self, item, itemType, price, itemImage, upgradeID = None, maxUpgrades = None, heal = 0, healCooldown = 0, showTitle = False):
        if itemType != ItemType.HEAL:
            data = {item : {'type' : itemType, 'image' : itemImage, 'price' : price, 'upgradeID' : upgradeID, 'maxUpgrades' : maxUpgrades}}
        else:
            data = {item : {'type' : itemType, 'image' : itemImage, 'price' : price, 'heal' : heal, 'healCooldown' : healCooldown, 'showTitle' : showTitle}}
        self.items.update(data)

    def removeItem(self, item):
        self.items.remove(item)

    def getItems(self):
        return self.items
    
    def updateTurretCount(self, amount):
        if self.shop:
            self.shop.updateTurrets(amount)

    @abc.abstractmethod
    def setupClerk(self):
        pass

    def deleteClerk(self):
        if self.clerk:
            self.clerk.disable()
            self.clerk.delete()
            self.clerk = None

    def setClerkChat(self, msgId):
        msgs = [CIGlobals.ShopGoodbye, CIGlobals.ShopNoMoney]
        if self.clerk: self.clerk.setChat(msgs[msgId])

    def __initShopCollisions(self, colName):
        self.notify.debug('Setting up shop collisions')
        shopSphere = CollisionSphere(0, 0, 0, 5)
        shopSphere.setTangible(0)
        shopNode = CollisionNode(colName)
        shopNode.addSolid(shopSphere)
        shopNode.setCollideMask(CIGlobals.WallBitmask)
        self.shopNP = self.attachNewNode(shopNode)
        self.shopNP.setZ(3)
        self.acceptOnce('enter' + self.shopNP.node().getName(), self.__handleShopCollision)

    def __handleShopCollision(self, entry):
        self.notify.debug('Entered collision sphere.')
        self.d_requestEnter()

    def d_requestHealth(self, health):
        self.sendUpdate('requestHealth', [health])

    def d_requestEnter(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestEnter', [])

    def d_requestExit(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestExit', [])

    @abc.abstractmethod
    def enterAccepted(self):
        pass

    def exitAccepted(self):
        self.cr.playGame.getPlace().fsm.request('walk')
        self.acceptOnce('enter' + self.shopNP.node().getName(), self.__handleShopCollision)
        self.inShop = False

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.__initShopCollisions('shopSphere' + str(self.doId))
        self.setupClerk()
        self.setParent(CIGlobals.SPRender)

    def destroy(self):
        if self.shop:
            self.shop.destroy()
        self.deleteClerk()
        self.inShop = False
        self.shopNP = None

    def disable(self):
        DistributedNode.disable(self)
        self.destroy()

    def delete(self):
        DistributedNode.delete(self)
        self.destroy()

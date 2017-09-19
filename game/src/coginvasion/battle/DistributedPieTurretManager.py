"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedPieTurretManager.py
@author Brian Lach
@date June 14, 2015
@author Maverick Liberty
@date August 10, 2015

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DirectWaitBar, OnscreenImage
from direct.task.Task import Task

from src.coginvasion.globals import CIGlobals

class DistributedPieTurretManager(DistributedObject):
    notify = directNotify.newCategory('DistributedPieTurretManager')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.myTurret = None
        self.guiFrame = None
        self.guiLabel = None
        self.guiBar = None
        self.guiBg = None
        self.turretGag = None

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        base.taskMgr.add(self.__pollMyBattle, '__pollMyBattle')

    def disable(self):
        base.taskMgr.remove("DPTM.pollTurret")
        base.taskMgr.remove("__pollMyBattle")
        if hasattr(self, 'makeTurretBtn'):
            self.makeTurretBtn.destroy()
            del self.makeTurretBtn
        self.destroyGui()
        self.myTurret = None
        if base.localAvatar.getMyBattle():
            base.localAvatar.getMyBattle().setTurretManager(None)
        DistributedObject.disable(self)
        
    def clearTurret(self):
        self.turret = None

    def __pollTurret(self, turretId, task):
        turret = self.cr.doId2do.get(turretId)
        if turret != None:
            self.myTurret = turret
            self.myTurret.b_setGag(self.turretGag)
            self.turretGag = None
            self.acceptOnce(turret.getDeathEvent(), self.clearTurret)
            self.makeGui()
            return Task.done
        return Task.cont
    
    def setGag(self, upgradeId):
        self.turretGag = upgradeId

    def d_requestPlace(self, posHpr):
        self.sendUpdate('requestPlace', [posHpr])

    def turretPlaced(self, turretId):
        base.taskMgr.add(self.__pollTurret, 'DPTM.pollTurret', extraArgs = [turretId], appendTask = True)

    def yourTurretIsDead(self):
        base.taskMgr.remove('DPTM.pollTurret')
        self.destroyGui()
        self.myTurret = None
        if base.localAvatar.getPUInventory()[0] > 0:
            self.createTurretButton()

    def makeGui(self):
        self.destroyGui()
        self.guiFrame = DirectFrame(parent = base.a2dBottomRight, pos=(-0.55, 0, 0.15))
        self.guiBg = OnscreenImage(image = "phase_4/maps/turret_gui_bg.png", scale = (0.15, 0, 0.075), parent = self.guiFrame)
        self.guiBg.setTransparency(True)
        self.guiLabel = DirectLabel(text = "Turret", text_fg = (1, 0, 0, 1), relief = None, text_scale = 0.05, text_font = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf"), pos = (0, 0, 0.025), parent = self.guiFrame)
        self.guiBar = DirectWaitBar(range = self.myTurret.getMaxHealth(), value = self.myTurret.getHealth(), scale = 0.125, parent = self.guiFrame, pos = (0, 0, -0.01))

    def createTurretButton(self):
        self.makeTurretBtn = DirectButton(
            relief = None,
            geom = CIGlobals.getDefaultBtnGeom(),
            text = 'Turret',
            text_scale = 0.055,
            command = self.handleMakeTurretBtn,
            pos = (-0.47, 0, 0.1),
            geom_scale = (0.5, 1.0, 1.0),
            text_pos = (0, -0.01),
            parent = base.a2dBottomRight
        )
        
        if base.localAvatar.getPUInventory()[0]:
            self.setGag(base.localAvatar.getPUInventory()[1])

    def handleMakeTurretBtn(self):
        self.makeTurretBtn.destroy()
        del self.makeTurretBtn
        x, y, z = base.localAvatar.getPos()
        h, p, r = base.localAvatar.getHpr()
        self.d_requestPlace([x, y, z, h, p, r])
        base.localAvatar.sendUpdate('usedPU', [0])

    def __pollMyBattle(self, task):
        if base.localAvatar.getMyBattle():
            base.localAvatar.getMyBattle().setTurretManager(self)
            if base.localAvatar.getPUInventory()[0] > 0:
                self.createTurretButton()
            return Task.done
        return Task.cont

    def destroyGui(self):
        if self.guiBar:
            self.guiBar.destroy()
            self.guiBar = None
        if self.guiLabel:
            self.guiLabel.destroy()
            self.guiLabel = None
        if self.guiBg:
            self.guiBg.destroy()
            self.guiBg = None
        if self.guiFrame:
            self.guiFrame.destroy()
            self.guiFrame = None

    def updateTurretGui(self):
        if self.guiBar:
            self.guiBar.update(self.myTurret.getHealth())
            
    def getTurret(self):
        return self.myTurret

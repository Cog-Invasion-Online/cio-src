"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file QuestRewardFrame.py
@author Maverick Liberty
@date September 17, 2017

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiBase import DGG

from panda3d.core import TextNode, TransparencyAttrib

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quest import QuestGlobals
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.gui.LaffOMeter import LaffOMeter

class QuestRewardFrame(DirectFrame):
    notify = directNotify.newCategory('QuestRewardFrame')
    
    def __init__(self, poster, reward, **kw):
        optiondefs = (('relief', None, None),
         ('image', QuestGlobals.getJBIcon(), None),
         ('image_scale', QuestGlobals.JB_JAR_SCALE, None),
         ('state', DGG.NORMAL, None))
        self.defineoptions(kw, optiondefs)
        
        # Finally, initialize the DirectFrame.
        DirectFrame.__init__(self, parent = poster, relief = None)
        self.initialiseoptions(QuestRewardFrame)
        self.reward = reward
        
        gagShopGeom = loader.loadModel('phase_4/models/gui/gag_shop_purchase_gui.bam')
        self.info = DirectFrame(parent = self,
            relief = None,
            geom = gagShopGeom.find('**/Char_Pnl'),
            geom_scale = (0.15, 0, 0.1275),
            text = '0',
            text_font = CIGlobals.getToonFont(),
            text_scale = 0.04,
            text_fg = (0, 0, 0, 1),
            text_align = TextNode.ACenter,
            text_pos = (0, -0.01),
        pos = (0, 0, -0.06))
        self.info.setBin('gui-popup', 40)
        
        gagShopGeom.removeNode()
        self.hide()
        
    def setup(self):
        if self.reward.rewardType == 1:
            # This is a jellybeans reward.
            self.setPos(QuestGlobals.LEFT_JB_JAR_POS)
            self.info['text'] = str(self.reward.rewardValue)
        elif self.reward.rewardType == 2:
            # This is a teleport access reward.
            self['image'] = QuestGlobals.getTPAccessIcon()
            self['image_scale'] = QuestGlobals.TP_ACCESS_SCALE
            self.setPos(QuestGlobals.LEFT_TP_ACCESS_POS)
            self.info['text'] = ZoneUtil.ZoneId2HoodAbbr[self.reward.rewardValue]
            self.info.setPos(-0.0025, 0, -0.04)
        elif self.reward.rewardType == 3:
            # This is a laff boost reward.
            r, g, b, _ = base.localAvatar.getHeadColor()
            hp = base.localAvatar.getMaxHealth() + self.reward.rewardValue
            laffMeter = LaffOMeter()
            laffMeter.generate(r, g, b, base.localAvatar.getAnimal(), maxHP = hp, initialHP = hp)
            self['image'] = laffMeter
            self['image_scale'] = QuestGlobals.LAFF_METER_SCALE
            self.setPos(QuestGlobals.LEFT_LAFF_METER_POS)
            self.info['text'] = '+%d' % self.reward.rewardValue
            self.info.setPos(0, 0, -0.05)
            laffMeter.destroy()
        elif self.reward.rewardType == 5:
            # This is a gag slot reward.
            icon = QuestGlobals.getGagSlotIcon(self.reward.rewardValue)
            self['image'] = icon
            self['image_scale'] = QuestGlobals.GAG_SLOT_ICON_SCALE
            self.setTransparency(TransparencyAttrib.MAlpha)
            self.setPos(QuestGlobals.LEFT_GAG_SLOT_POS)
            self.info.hide()
            
        self.show()
        
    def destroy(self):
        if hasattr(self, 'reward'):
            self.info.destroy()
            del self.info
            del self.reward
            DirectFrame.destroy(self)
        
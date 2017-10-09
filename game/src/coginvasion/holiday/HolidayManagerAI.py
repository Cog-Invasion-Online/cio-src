"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HolidayManagerAI.py
@author Maverick Liberty
@date March 14, 2017

"""

from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class HolidayManagerAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory('HolidayManagerAI')
    
    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)
        self.holiday = 0
        
    def setHoliday(self, holiday):
        self.holiday = holiday
        
    def d_srvRequestHoliday(self):
        self.sendUpdate('srvRequestHoliday', [])

"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HolidayManagerUD.py
@author Maverick Liberty
@date November 13, 2015

"""

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify

class HolidayManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('HolidayManagerUD')
    
    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        
    def setHoliday(self, holiday):
        self.holiday = holiday
        
    def requestHoliday(self):
        sender = self.air.getAccountIdFromSender()
        self.sendUpdateToAccountId(sender, 'setHoliday', [self.holiday])
        
    def srvRequestHoliday(self):
        # Our good ol' pal, AI, is requesting the current holiday.
        sender = self.air.getMsgSender()
        self.sendUpdateToChannel(sender, 'setHoliday', [self.holiday])
        
    def delete(self):
        del self.holiday
        DistributedObjectGlobalUD.delete(self)

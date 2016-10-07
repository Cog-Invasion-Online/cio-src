# Filename: HolidayManager.py
# Created by:  DecodedLogic (13Nov15)

from pandac.PandaModules import VirtualFileSystem, Filename

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify

class HolidayType:

    CHRISTMAS = 1
    HALLOWEEN = 2

class HolidayGlobals:
    CHRISTMAS_TIME = "Happy Winter Holidays! Winter has struck Toontown!"
    COACH_GREETING = "Happy Holidays, %s! Here, take some snowballs!"

class HolidayManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('HolidayManager')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        return

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)
        self.sendUpdate('requestHoliday', [])

    def setHoliday(self, holiday):
        self.holiday = holiday
        if holiday == HolidayType.CHRISTMAS:
            # Load the winter multifile.
            vfs = VirtualFileSystem.getGlobalPtr()
            vfs.mount(Filename('winter.mf'), '.', VirtualFileSystem.MFReadOnly)

    def getHoliday(self):
        return self.holiday

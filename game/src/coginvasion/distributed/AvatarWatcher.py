"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AvatarWatcher.py
@author Maverick Liberty
@date October 2, 2018

This is a utility module that is supposed to "watch" and pay attention to
avatars so that a subclass, such as a DistributedNPCToonAI, could be notified
when an avatar has left its sphere of influence which could be from the player
changing zones, unexpectedly disconnecting, etc.

"""

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

DELETED = 0
ZONE_CHANGE = 1
DIED = 2

REASON_ID_2_REASON = {
    DELETED : "Deleted",
    ZONE_CHANGE : "Changed Zones",
    DIED : "Died"
}

class AvatarInstance(DirectObject):
    
    def __init__(self, av, watcher):
        DirectObject.__init__(self)
        
        self.avatar = av
        self.avId = av.doId
        self.watcher = watcher
        
        self.accept(av.getDeleteEvent(), self.__onPreDelete)
        self.accept(av.getLogicalZoneChangeEvent(), self.__onZoneChange)
        self.accept(av.getHealthChangeEvent(), self.__onHealthChange)
        
    def __onHealthChange(self, newHealth, oldHealth):
        self.watcher._avatarChangeHealthEvent(self, newHealth, oldHealth)
        
    def __onZoneChange(self, newZone, oldZone):
        self.watcher._avatarSwitchZonesEvent(self, newZone, oldZone)
        
    def __onPreDelete(self):
        self.watcher._avatarPredeleteEvent(self)
        
    def cleanup(self):
        self.ignoreAll()
        self.avatar = None
        self.avId = None
        self.watcher = None

class AvatarWatcher(DirectObject):
    """
    Utility class that listens for when an avatar is deleted or changes health or zone.
    NOTE: This class referers to the PLAYER avatars, not NPC avatars like Suits.
    """
    
    STOP_TRACKING_WHEN_DEAD = 0
    
    def __init__(self, air, zoneId=None):
        DirectObject.__init__(self)
        self.air = air
        
        # We want to have a useful notifier name so we can easily identify where issues are arising from.
        self.notify = directNotify.newCategory('{0}::AvatarWatcher'.format(self.__class__.__name__))

        # This is a list of the avatar ids we're watching.
        self.watchingAvatarIds = []
        self.avId2instance = {}
        
        # This is the zone ID we're working in.
        self.zoneId = zoneId
        
        assert self.air != None, "Must have a valid pointer to AI!"
        
    def getAvatarInstance(self, avId):
        return self.avId2instance.get(avId, None)
    
    def isTrackingAvatarId(self, avId):
        """ Checks if we're currently tracking or watching the avatar id provided """
        return (avId != None and avId in self.watchingAvatarIds and self.avId2instance.has_key(avId))
    
    def startTrackingAvatarId(self, avId):
        """ If given an avatar id not already being tracked, it will add it to
        `watchingAvatarIds` and start listening to events emitted by the avatar """
        if not self.isTrackingAvatarId(avId) and self.idPointsToValidAvatar(avId):
            avatar = self.air.doId2do.get(avId, None)
            
            self.watchingAvatarIds.append(avId)
            
            inst = AvatarInstance(avatar, self)
            self.avId2instance[avId] = inst
            
    def stopTrackingAvatarId(self, avId, removeFromList = True):
        """ If given an avatar id currently being tracked, let's stop tracking it,
        stop listening to events emitted by the avatar, and remove it from our cache. """
        if self.isTrackingAvatarId(avId) and self.idPointsToValidAvatar(avId):
            # Let's clean up the AvatarInstance we're storing first.
            inst = self.avId2instance[avId]
            inst.cleanup()
            del self.avId2instance[avId]
            if removeFromList:
                self.watchingAvatarIds.remove(avId)
        else:
            self.notify.debug('Avatar ID {0} is not currently being tracked and/or the avatar assigned to it has regressed.'.format(avId))
            
    def stopTrackingAll(self):
        """ This method will stop tracking each avatar id and clear our `watchingAvatarIds`
        cache. """
        
        for avId in self.watchingAvatarIds:
            self.stopTrackingAvatarId(avId, False)
            
        self.watchingAvatarIds = []
        self.avId2instance = {}
            
    def handleAvatarLeave(self, avatar, reason):
        """ This method is called whenever an avatar leaves our sphere of influence and
        should be reimplemented in subclasses. (The whole point of this class is for a subclass to
        utilize this functionality. """
        self.notify.debug('Avatar ID {0} has left our sphere of influence because of {1}'
                          .format(
                              avatar.doId, 
                              REASON_ID_2_REASON.get(reason, "Unknown")
                           )
        )
        raise NotImplementedError("Subclasses should override and implement this method so our tracking has substance.")
    
    def handleAvatarChangeHealth(self, avatar, newHealth, prevHealth):
        """ This function could be useful in certain circumstances. Please note that
        by default, when a player dies, #handleAvatarLeave() will be called as well. This
        all depends on whether `STOP_TRACKING_WHEN_DEAD` is true or not. """
        
        raise NotImplementedError("Subclasses should override this method to be alerted when a tracked avatar changes health.")
            
    def _avatarPredeleteEvent(self, inst):
        """ This function is called when one of the avatars we're tracking has
        let us know it is about to be deleted. This function will automatically stop
        tracking the avatar in question as well. """
        
        avatar = inst.avatar
        avId = inst.avId
        
        self.handleAvatarLeave(avatar, DELETED)
        self.stopTrackingAvatarId(avId)
        self.notify.debug('Avatar ID {0} is about to be deleted.'.format(avId))
        
    def _avatarSwitchZonesEvent(self, inst, newZoneId, oldZoneId):
        """ This function is called when one of the avatars we're tracking has
        let us know that it is switching zones. This function will automatically stop
        tracking the avatar in question if the zoneId differs from ours or a zoneId
        hasn't been specified in this class. """
        
        avatar = inst.avatar
        avId = inst.avId

        self.notify.debug('Avatar ID {0} is switching from ZoneId {1} -> ZoneId {2}.'
                          .format(avId, oldZoneId, newZoneId))
        
        if self.zoneId == None or newZoneId != self.zoneId:
            self.handleAvatarLeave(avatar, ZONE_CHANGE)
            self.stopTrackingAvatarId(avId)
            
    def _avatarChangeHealthEvent(self, inst, newHealth, prevHealth):
        """ This function is called when one of the avatars we're tracking has
        let us know that it has changed health. This is useful when a subclass needs
        to know whenever an avatar has died or if their health reaches a certain quantity.
        Default behavior is that once an avatar has died, we stop tracking them and say that the player
        has left our sphere of influence. """
        
        avatar = inst.avatar
        avId = inst.avId
        
        self.handleAvatarChangeHealth(avatar, newHealth, prevHealth)
        if avatar.isDead() and self.STOP_TRACKING_WHEN_DEAD:
            self.handleAvatarLeave(avatar, DIED)
            self.stopTrackingAvatarId(avId)
            self.notify.debug("Avatar ID {0} has died, so we're going to stop tracking them by default.".format(avId))
        
    def idPointsToValidAvatar(self, avId):
        """ Checks to see if the provided avatar ID points to a non-None avatar object """
        return (self.air != None and self.air.doId2do.get(avId, None) != None)
        

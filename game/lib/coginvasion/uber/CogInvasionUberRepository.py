"""

  Filename: CogInvasionUberRepository.py
  Created by: DuckyDuck1553 (03Dec14)

"""

from lib.coginvasion.distributed.CogInvasionInternalRepository import CogInvasionInternalRepository
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.distributed.DistributedRootAI import DistributedRootAI
from lib.coginvasion.distributed.CogInvasionDoGlobals import *
from direct.distributed.ParentMgr import ParentMgr
from LoginToken import LoginToken
from LoginServerConnection import LoginServerConnection

STORE_LOGIN_TOKEN = 100

class CogInvasionUberRepository(CogInvasionInternalRepository):
    notify = directNotify.newCategory("CIUberRepository")
    GameGlobalsId = DO_ID_COGINVASION

    def __init__(self, baseChannel, serverId):
        CogInvasionInternalRepository.__init__(self, baseChannel, serverId,
                    ['resources/phase_3/etc/direct.dc', 'resources/phase_3/etc/toon.dc'], dcSuffix='UD')
        self.notify.setInfo(True)
        self.activeTokens = []
        self.parentMgr = ParentMgr()
        self.holiday = 0
        
        # Let's start the login server connection server.
        self.loginServerConn = LoginServerConnection(self, 9001)

    def getParentMgr(self, zone):
        return self.parentMgr

    def handleDatagram(self, di):
        msgType = self.getMsgType()
        if msgType == STORE_LOGIN_TOKEN:
            self.__handleLoginToken(di)
        else:
            CogInvasionInternalRepository.handleDatagram(self, di)

    def __handleLoginToken(self, di):
        token = di.getString()
        ip = di.getString()
        tokenObj = LoginToken(token, ip)
        self.storeToken(tokenObj)

    # Validate a login token.
    def isValidToken(self, token, ip):
        # Begin the process of validating this token.
        if token in self.activeTokens:
            # Let's make sure this token is for this IP.
            if token.getIP() == ip:
                # We've got a match!
                self.deleteToken(token)
                return 1
        elif ip == '0.0.0.0:0':
            return 1
        return 0


    def storeToken(self, tokenObj):
        """
        Store and activate a new login token.
        """

        # Begin the process of storing this token.

        for token in self.activeTokens:

            # Is there already an active token object on this ip?
            if token.getIP() == tokenObj.getIP():
                # If so, deactivate the old token.
                self.deleteToken(token)

            # Token objects with matching tokens are okay, as long as the
            # IP addresses do not match on both objects. Matching IPs
            # would have already been detected from the code above.

        # If we've made it this far, we can finally store the token.

        # First, add the token to the activeTokens list.
        self.activeTokens.append(tokenObj)
        print "Activated token: %s, IP: %s" % (tokenObj.getToken(), tokenObj.getIP())

        # Then, start the deactivateToken task.
        taskMgr.doMethodLater(self.getActiveTokenLength(), self.deleteTokenTask, 
            tokenObj.getDeleteTask(), extraArgs = [tokenObj], appendTask = True)

        # We're done! Tell the LauncherLoginManager.
        return 1

    def deleteTokenTask(self, obj, task):
        self.deleteToken(obj)
        return task.done

    def deleteToken(self, token):
        """
        Delete an active login token from the activeTokens list.
        """

        # First, stop the deactivate task.
        taskMgr.remove(token.getDeleteTask())

        print "Deactivated token: %s, IP: %s" % (token.getToken(), token.getIP())

        # Next, cleanup the object.
        token.cleanup()

        # Finally, remove the object from the activeTokens list.
        self.activeTokens.remove(token)

    def isBanned(self, ip):
        return False

    def getActiveTokenLength(self):
        # How long (in seconds) a login token can be active.
        return 300

    def handleConnected(self):
        rootObj = DistributedRootAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        self.createObjects()
        self.notify.info('Successfully started Cog Invasion Online Uber Repository!')

    def createObjects(self):
        self.csm = self.generateGlobalObject(DO_ID_CLIENT_SERVICES_MANAGER,
                                'ClientServicesManager')
        self.dnm = self.generateGlobalObject(DO_ID_DISTRICT_NAME_MANAGER,
                                'DistrictNameManager')
        self.friendsManager = self.generateGlobalObject(DO_ID_FRIENDS_MANAGER,
                                'FriendsManager')
        self.holidayManager = self.generateGlobalObject(DO_ID_HOLIDAY_MANAGER,
                                'HolidayManager')
        self.holidayManager.setHoliday(self.holiday)
        self.nsm = self.generateGlobalObject(DO_ID_NAME_SERVICES_MANAGER,
                                'NameServicesManager')

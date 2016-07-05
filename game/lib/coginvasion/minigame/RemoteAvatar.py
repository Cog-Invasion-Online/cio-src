"""

  Filename: RemoteAvatar.py
  Created by: blach (28Apr15)

"""

from panda3d.core import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals

class RemoteAvatar:

    notify = directNotify.newCategory("RemoteAvatar")

    def __init__(self, mg, cr, avId):
        self.mg = mg
        self.cr = cr
        self.avId = avId
        self.avatar = None
        self.teamText = None
        self.team = None

    def setTeam(self, team):
        self.team = team
        if self.teamText:
            self.teamText.removeNode()
            self.teamText = None
        textNode = TextNode('teamText')
        textNode.setAlign(TextNode.ACenter)
        textNode.setFont(CIGlobals.getMickeyFont())
        self.teamText = self.avatar.attachNewNode(textNode)
        self.teamText.setBillboardAxis()
        self.teamText.setZ(self.avatar.getNameTag().getZ() + 1.0)
        self.teamText.setScale(5.0)

    def getTeam(self):
        return self.team

    def retrieveAvatar(self):
        self.avatar = self.cr.doId2do.get(self.avId, None)
        self.avatar.setPythonTag('player', self.avId)
        if not self.avatar:
            self.notify.warning("Tried to create a " + self.__class__.__name__ + " when the avatar doesn't exist!")
            self.avatar = None

    def cleanup(self):
        del self.avatar
        del self.avId
        del self.cr
        del self.mg
        if self.teamText:
            self.teamText.removeNode()
            self.teamText = None
        del self.team

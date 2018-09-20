from Entity import Entity

class InfoPlayerRelocate(Entity):

    def Relocate(self):
        print "relocating local avatar"
        base.localAvatar.setPos(self.cEntity.getOrigin())
        base.localAvatar.setHpr(self.cEntity.getAngles())
        base.localAvatar.d_broadcastPositionNow()
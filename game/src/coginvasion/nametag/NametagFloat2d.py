from pandac.PandaModules import Point3

from NametagFloat3d import NametagFloat3d


class NametagFloat2d(NametagFloat3d):
    def doBillboardEffect(self):
        pass

    def update(self):
        NametagFloat3d.update(self)

        self.updateClickRegion()

    def setClickRegionFrame(self, left, right, bottom, top):
        mat = self.contents.getNetTransform().getMat()

        left, _, top = mat.xformPoint(Point3(left, 0, top))
        right, _, bottom = mat.xformPoint(Point3(right, 0, bottom))

        self.region.setFrame(left, right, bottom, top)

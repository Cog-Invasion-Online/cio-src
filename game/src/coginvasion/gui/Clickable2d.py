from panda3d.core import Point3

from Clickable import Clickable


class Clickable2d(Clickable):
    def setClickRegionFrame(self, left, right, bottom, top):
        mat = self.contents.getNetTransform().getMat()

        left, _, top = mat.xformPoint(Point3(left, 0, top))
        right, _, bottom = mat.xformPoint(Point3(right, 0, bottom))

        self.region.setFrame(left, right, bottom, top)

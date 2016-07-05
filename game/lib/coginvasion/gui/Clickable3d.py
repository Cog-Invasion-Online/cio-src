from panda3d.core import Quat, Point3, Point2

from Clickable import Clickable


class Clickable3d(Clickable):
    def setClickRegionFrame(self, left, right, bottom, top):
        transform = self.contents.getNetTransform()

        # We use the inverse of the cam transform so that it will not be
        # applied to the frame points twice:
        camTransform = base.cam.getNetTransform().getInverse()

        # Compose the inverse of the cam transform and our node's transform:
        transform = camTransform.compose(transform)

        # Discard its rotational components:
        transform.setQuat(Quat())

        # Transform the frame points into cam space:
        mat = transform.getMat()
        camSpaceTopLeft = mat.xformPoint(Point3(left, 0, top))
        camSpaceBottomRight = mat.xformPoint(Point3(right, 0, bottom))

        # Project into screen space:
        screenSpaceTopLeft = Point2()
        screenSpaceBottomRight = Point2()
        base.camLens.project(Point3(camSpaceTopLeft), screenSpaceTopLeft)
        base.camLens.project(Point3(camSpaceBottomRight), screenSpaceBottomRight)

        left, top = screenSpaceTopLeft
        right, bottom = screenSpaceBottomRight

        self.region.setFrame(left, right, bottom, top)

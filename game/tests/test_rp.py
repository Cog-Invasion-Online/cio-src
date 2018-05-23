from panda3d.core import *
loadPrcFile("config/Confauto.prc")
loadPrcFileData("", "load-display pandagl")
loadPrcFileData("", "audio-library-name none")

from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from direct.gui.DirectGui import OnscreenImage

class TestBase(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)
        depth = Texture("depth")
        depth.setWrapU(Texture.WMClamp)
        depth.setWrapV(Texture.WMClamp)
        self.fmgr = FilterManager(self.win, self.cam)
        depthQuad = self.fmgr.renderQuadInto(depthtex = depth)
        #depthQuad.hide()
        smiley = loader.loadModel("models/smiley.egg.pz")
        smiley.reparentTo(render)
        img = OnscreenImage(image = depth, scale = 0.3, pos = (0, 0, -0.7))

base = TestBase()
base.run()
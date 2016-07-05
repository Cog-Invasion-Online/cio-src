from panda3d.core import *

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("render_pipeline.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)

loadPrcFile('config/config_client.prc')
loadPrcFile("Config/configuration.prc")

from Code.RenderingPipeline import RenderingPipeline
from Code.DirectionalLight import DirectionalLight
#from Code.GlobalIllumination import GlobalIllumination

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()


rp = RenderingPipeline(base)
#rp.getMountManager().setBasePath(".")
rp.loadSettings("Config/pipeline.ini")
rp.create()

dLight = DirectionalLight()
dLight.setDirection(Vec3(60, 30, 100))
dLight.setShadowMapResolution(2048)
dLight.setAmbientColor(Vec3(0.0, 0.0, 0.0))
dLight.setPos(Vec3(60, 30, 100))
dLight.setColor(Vec3(3))
dLight.setPssmTarget(base.cam, base.camLens)
dLight.setCastsShadows(True)
rp.addLight(dLight)
rp.setGILightSource(dLight)

scene = loader.loadModel("../phase_3/models/gui/quit_button.bam")
scene.reparentTo(render)
scene.setScale(5)

scene.setShader(
	rp.getDefaultObjectShader(False))

rp.reloadShaders()

base.run()

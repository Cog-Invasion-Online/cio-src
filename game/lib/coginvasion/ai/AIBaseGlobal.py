from AIBase import AIBase
from direct.directnotify.DirectNotifyGlobal import directNotify
from pandac.PandaModules import RescaleNormalAttrib, NodePath, Notify

__builtins__['base'] = AIBase()
__builtins__['ostream'] = Notify.out()
__builtins__['run'] = base.run
__builtins__['taskMgr'] = base.taskMgr
__builtins__['jobMgr'] = base.jobMgr
__builtins__['eventMgr'] = base.eventMgr
__builtins__['messenger'] = base.messenger
__builtins__['bboard'] = base.bboard
__builtins__['config'] = base.config
__builtins__['directNotify'] = directNotify
render = NodePath('render')
render.setAttrib(RescaleNormalAttrib.makeDefault())
render.setTwoSided(0)
__builtins__['render'] = render
from direct.showbase import Loader
base.loader = Loader.Loader(base)
__builtins__['loader'] = base.loader
directNotify.setDconfigLevels()

def inspect(anObject):
    from direct.tkpanels import Inspector
    Inspector.inspect(anObject)


__builtins__['inspect'] = inspect
taskMgr.finalInit()

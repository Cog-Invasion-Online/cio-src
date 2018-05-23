from panda3d.core import *
loadPrcFile('config/config_client.prc')

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("resources/phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("resources/phase_14.mf"), ".", VirtualFileSystem.MFReadOnly)

from direct.showbase.ShowBase import ShowBase

base = ShowBase()

base.startTk()

from direct.tkpanels.ParticlePanel import ParticlePanel

pp = ParticlePanel()             # Create the panel

base.run()
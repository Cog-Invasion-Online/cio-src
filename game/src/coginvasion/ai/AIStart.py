"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AIStart.py
@author Brian Lach
@date December 14, 2014

"""

import __builtin__

__builtin__.process = 'ai'

__builtin__.__dict__.update(__import__('panda3d.core', fromlist=['*']).__dict__)

import sys
sys.dont_write_bytecode = True

#from src.coginvasion.base import Logger
#logger = Logger.Starter(log_prefix = 'ai-', path = 'astron/district_logs')
#logger.startNotifyLogging()

from panda3d.core import loadPrcFile, loadPrcFileData, VirtualFileSystem, PStatClient

loadPrcFileData('', 'model-path ./resources')

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

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.')
parser.add_argument('--max-channels', help='The number of channels the server may use.')
parser.add_argument('--stateserver', help="The control channel of this UD's designated State Server.")
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.")
parser.add_argument('--eventlogger-ip', help="The IP address of the Astron Event Logger to log to.")
parser.add_argument('config', nargs='*', default = ['config/config_server.prc'], help = "PRC file(s) to load.")
args = parser.parse_args()
__builtins__.args = args

for prc in args.config:
	loadPrcFile(prc)

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s000000\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
loadPrcFileData('Command-line', localconfig)

from src.coginvasion.base.Metadata import Metadata
__builtins__.metadata = Metadata()
metadata.PROCESS = 'server'
metadata.DEDICATED_SERVER = True

loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name none')

#PStatClient.connect("127.0.0.1")

from direct.showbase.ShowBase import ShowBase
base = ShowBase()
# Limit server to a certain number of ticks per second
#base.setSleep(1 / base.config.GetFloat('server-ticks', 30))

from p3recastnavigation import RNNavMeshManager

nmMgr = RNNavMeshManager.get_global_ptr()
nmMgr.set_root_node_path(render)
nmMgr.get_reference_node_path().reparentTo(render)
nmMgr.start_default_update()
nmMgr.get_reference_node_path_debug().reparentTo(render)
base.nmMgr = nmMgr

# We deal with attacks on the server side as well
from src.coginvasion.attack import AttackClasses
base.attackMgr = AttackClasses.AttackManager()

from direct.distributed.ClockDelta import globalClockDelta
__builtins__.globalClockDelta = globalClockDelta

from src.coginvasion.ai.CogInvasionAIRepository import CogInvasionAIRepository as CIAIR
base.air = CIAIR(config.GetInt('air-base-channel', 401000000), config.GetInt('air-stateserver', 10000))
host = args.astron_ip
port = 7033
if ':' in host:
	host, port = args.astron_ip.split(':', 1)
	port = int(port)
base.air.connect(host, port)

try:
	base.run()
except SystemExit:
	raise

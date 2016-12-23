########################################
# Filename: AIStart.py
# Created by: blach (14Dec14)
########################################

import __builtin__

__builtin__.process = 'ai'

__builtin__.__dict__.update(__import__('pandac.PandaModules', fromlist=['*']).__dict__)

import sys
sys.dont_write_bytecode = True

from pandac.PandaModules import loadPrcFile, loadPrcFileData, VirtualFileSystem

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)

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

class game:
	name = 'coginvasion'
	process = 'server'
__builtins__.game = game

loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-library-name none')

from direct.showbase.ShowBase import ShowBase
base = ShowBase()
base.setSleep(0.04)

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

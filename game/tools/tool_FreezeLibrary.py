"""
  
  Filename: tool_FreezeLibrary.py
  Created: DuckyDuck1553 (5Nov14)
  
"""

import os, argparse

print os.environ.get("panda")

parser = argparse.ArgumentParser(description = "Freeze the Cog Invasion Online library into a .PYD file.")
parser.add_argument("--panda", default = "C:/Users/Public/Documents/panda3d/Panda3D-CI", help = "The Panda3D directory.")
parser.add_argument("--output", default = "C:/Users/Public/Documents/panda3d/build_test/tools/libcoginvasion.pyd",
			help = "The file that will come out.")
parser.add_argument("--modules", nargs='*', default = ['direct', 'lib.toontown'],
			help = "The modules to include in the output file.")
parser.add_argument("--main", default = '__main__',
			help = "The starting file.")
args = parser.parse_args()

fileType = raw_input("DLL or EXE?: ")
fileType = fileType.upper()
if fileType != "EXE":
	fileType = ''

print "Freezing..."

cmd = os.path.join(args.panda, "python\ppython.exe")
cmd += ' -m direct.showutil.pfreeze%s' % fileType
for module in args.modules:
	cmd += " -i {0}.*.*".format(module)
cmd += " -i {0}.*".format('encodings')
cmd += " -i {0}".format('base64')
cmd += " -i {0}".format('site')
cmd += " -o {0}".format(args.output)
cmd += " -x {0}".format("panda3d")
cmd += " {0}".format(args.main)

os.system(cmd)

print "Freezing complete."


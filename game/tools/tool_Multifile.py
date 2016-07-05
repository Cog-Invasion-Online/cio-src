"""

  Filename: tool_Multifile.py
  Created by: DuckyDuck1553 (6Nov14)
  
"""

import os, argparse, glob

parser = argparse.ArgumentParser(description = "Do things with a multifile.")
parser.add_argument("--filename", default = "phase_3.mf", help = "The file to be used.")
parser.add_argument("--mtype", default = "compile", help = "Compile or decompile.")
args = parser.parse_args()

def do(mtype, filename):
	cmd = os.path.join("multify.exe")
	if mtype == "decompile":
		cmd += " -x -f %s" % filename
	elif mtype == "compile":
		cmd += " -c -f %s %s -p \"cio6-17-14_blach\"" % (filename, filename.replace(".mf", ""))
	os.system(cmd)

def do_all(mtype):
	for multifile in glob.glob("*.mf"):
		do(mtype, multifile)

if args.filename.lower() == "all":
	do_all(args.mtype.lower())
else:
	do(args.mtype.lower(), args.filename)
	
print "Done"
	
